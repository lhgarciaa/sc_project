#!/usr/bin/env python
import argparse
import os
import cic_outspector
import cic_utils
import sys
import cv2
import cic_overlap
import cPickle as pickle
import cic_plot
import datetime


def main():
    parser = argparse.ArgumentParser(description='Filters ROIs listed in '
                                     'input_csv out out of results written to '
                                     'output_csv and output_tif')
    parser.add_argument('-ic', '--input_csv',
                        help='Path to CSV containing ROIs to filter',
                        required=True)
    parser.add_argument('-cd', '--case_dir',
                        help='Directory to Connection Lens case',
                        required=True)
    parser.add_argument('-gcs', '--grid_cell_size',
                        required=True)
    parser.add_argument('-lvl', '--atlas_level',
                        help='Atlas level to write',
                        required=True)
    parser.add_argument('-ch', '--channel',
                        help='Case channel to write to output',
                        required=True)
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
                        action='store_true')

    args = vars(parser.parse_args())
    verbose = args['verbose']

    if verbose:
        print "{} {}\nargs {}".format(datetime.datetime.now(),
                                      sys.argv[0],
                                      args)

    input_csv_path = args['input_csv']
    if not os.path.isfile(input_csv_path):
        if verbose:
            print("No ROI filter CSV {}, exiting".format(input_csv_path))
            sys.exit(0)
    case_dir = args['case_dir']
    assert os.path.isdir(case_dir),\
        "no case dir {}".format(case_dir)
    ch = args['channel']
    overlap_ch_dir_path = cic_outspector.overlap_dir_path(
        case_dir=case_dir, ch=ch)
    assert os.path.isdir(overlap_ch_dir_path),\
        "no overlap dir {}".format(overlap_ch_dir_path)

    gcs = args['grid_cell_size']
    lvl = args['atlas_level']

    # get section from opairs.lst
    opairs_section = cic_outspector.opairs_section(case_dir=case_dir,
                                                   lvl=lvl)
    if verbose:
        print("Using level {} grid cell size {}".format(lvl, gcs))
        print("retrieved section {} from case dir {}".format(opairs_section,
                                                             case_dir))

    # check that we have section for ARA level, if not exit WITHOUT error
    #  idea is that we can call this from levels 1 - 132
    if opairs_section is None:
        print("No opairs.lst section found for ARA level {}".format(lvl))
        print("exiting without error")
        sys.exit(0)

    else:
        thresh_dir_path = cic_outspector.thresh_dir_path(
            case_dir=case_dir,
            ch=ch)
        assert os.path.isdir(thresh_dir_path), \
            "No threshold dir {}".format(thresh_dir_path)
        thresh_tif_path = cic_outspector.degenerate_or_thresh_tif_path(
            thresh_dir_path=thresh_dir_path,
            opairs_section=opairs_section,
            ch=ch)
        assert thresh_tif_path is not None, "threshold {} not found".format(
            thresh_tif_path)
        overlap_dir_path = cic_outspector.overlap_dir_path(
            case_dir=case_dir,
            ch=ch)
        assert os.path.isdir(overlap_dir_path), \
            "No overlap dir {}".format(overlap_dir_path)
        overlap_path = cic_outspector.cellcount_or_overlap_path(
            overlap_dir_path=overlap_dir_path,
            opairs_section=opairs_section,
            ch=ch,
            gcs=gcs)
        assert overlap_path is not None, "overlap {} not found".format(
            overlap_path)
        atlas_tif_path = cic_outspector.atlas_tif_path(lvl=lvl)
        assert atlas_tif_path is not None, "atlas tif {} not found".format(
            atlas_tif_path)
        # either include or exclude ROIs listed respectively in input_csv
        #  and write these results to output_csv and output_tif
        (roi_filter_overlap_tup, roi_filter_thresh_img) = \
            cic_outspector.roi_filter_thresh_ovlp(
            roi_filter_csv_path=input_csv_path,
            thresh_tif_path=thresh_tif_path,
            overlap_path=overlap_path,
            atlas_tif_path=atlas_tif_path,
            gcs=int(gcs),
            lvl=int(lvl),
            hemi='r',
            opairs_section=opairs_section,
            verbose=verbose)

        output_csv_path = cic_outspector.output_roi_filter_overlap_csv_path(
            overlap_dir_path=overlap_dir_path,
            overlap_path=overlap_path)
        output_img_path = cic_outspector.output_roi_filter_tif_path(
            thresh_dir_path=thresh_dir_path,
            thresh_tif_path=thresh_tif_path)

        cic_overlap.write_overlap_csv(overlap_tup=roi_filter_overlap_tup,
                                      output_csv_path=output_csv_path)
        cv2.imwrite(output_img_path, roi_filter_thresh_img)

        # for cases of retrograde output, write additional image since
        #  degenerate image is difficult to see
        visual_path = cic_outspector.visual_path(
                thresh_dir_path=thresh_dir_path,
                thresh_tif_path=output_img_path)

        grid_ref_tif_path = cic_outspector.grid_ref_tif_path(
             overlap_path=overlap_path, ch=ch)
        assert os.path.isfile(grid_ref_tif_path), \
            "No grid reference tif found {}".format(grid_ref_tif_path)

        grid_ref_img = cv2.imread(grid_ref_tif_path, cv2.IMREAD_UNCHANGED)

        if "degenerate" in output_img_path:
            eroded_roi_filter_thresh_img = cic_plot.erode(
                img=roi_filter_thresh_img)
            visual_img = cic_plot.compose(eroded_roi_filter_thresh_img,
                                          grid_ref_img)
        else:
            visual_img = cic_plot.compose(roi_filter_thresh_img,
                                          grid_ref_img)
        cv2.imwrite(visual_path, visual_img)

        if verbose:
            print("Wrote roi filtered overlap to {}".format(output_csv_path))
            print("Wrote roi filtered image  to {}".format(output_img_path))
            print("Wrote visual image  to {}".format(visual_path))

        output_pickle_path = cic_utils.pickle_path(output_csv_path)
        pickle.dump(args, open(output_pickle_path, "wb"))
        if verbose:
            print("Wrote pickle args to {}".format(output_pickle_path))
        output_pickle_path = cic_utils.pickle_path(output_img_path)
        pickle.dump(args, open(output_pickle_path, "wb"))
        if verbose:
            print("Also wrote pickle args to {}".format(output_pickle_path))


if __name__ == "__main__":
    main()
