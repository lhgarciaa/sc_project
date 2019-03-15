#!/usr/bin/env python
import argparse
import os
from cic_dis import cic_outspector
from cic_dis import cic_utils
import sys
import cv2
import cPickle as pickle
from cic_dis import cic_plot


def main():
    parser = argparse.ArgumentParser(description='Creates an atlas matching '
                                     'series of threshold images with '
                                     'labelling colored by community')
    parser.add_argument('-i', '--input_csv',
                        help='Path to CSV containing consensus community '
                        'structure ',
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
    parser.add_argument('-isc', '--injection_site_colors',
                        help='List of injection sites color tuples e.g. {}'
                        .format('-iso BLA_am::228:26:28 BLA_al::255:127:0'),
                        required=True,
                        nargs='+')
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
                        action='store_true')
    parser.add_argument('-aa', '--annotated_atlas',
                        help='Overlay over annotated atlas (i.e. with labels)',
                        action='store_true')

    args = vars(parser.parse_args())

    input_csv_path = args['input_csv']
    assert os.path.isfile(input_csv_path),\
        "can't find input csv file {}".format(input_csv_path)
    case_dir = args['case_dir']
    assert os.path.isdir(case_dir),\
        "no case dir {}".format(case_dir)
    ch = args['channel']
    # will do something like os.path.join(case_dir, 'overlap/{}'.format(ch))
    overlap_ch_dir_path = cic_outspector.overlap_dir_path(
        case_dir=case_dir,
        ch=ch)
    assert os.path.isdir(overlap_ch_dir_path),\
        "no overlap dir {}".format(overlap_ch_dir_path)

    gcs = args['grid_cell_size']
    lvl = args['atlas_level']
    inj_site_clr_lst = args['injection_site_colors']
    assert len(inj_site_clr_lst) > 0, "Invalid format for injection_site_colors {}".format(args['injection_site_colors'])  # NOQA
    for inj_site_tup in inj_site_clr_lst:
        assert '::' in inj_site_tup, \
            "Invalid injection site color tup {}".format(inj_site_tup)
        assert ':' in inj_site_tup, \
            "Invalid injection site color tup {}".format(inj_site_tup)
    (inj_site_clr_map, inj_site_lst) = cic_plot.parse_inj_site_clr_lst(
        inj_site_clr_lst=inj_site_clr_lst)

    verbose = args['verbose']
    annotated_atlas = args['annotated_atlas']

    # get section from opairs.lst
    opairs_section = cic_outspector.opairs_section(case_dir=case_dir,
                                                   lvl=lvl)

    # check that we have section for ARA level, if not exit WITHOUT error
    #  idea is that we can call this from levels 1 - 132
    if opairs_section is None:
        if verbose:
            print("No opairs.lst section found for ARA level {}".format(lvl))
            print("exiting without error")
        sys.exit(0)
    # else have opairs section now get threshold tif
    else:
        thresh_dir_path = cic_outspector.thresh_dir_path(
            case_dir=case_dir,
            ch=ch)
        thresh_tif_path = cic_outspector.roi_filter_or_thresh_tif_path(
            thresh_dir_path=thresh_dir_path,
            opairs_section=opairs_section,
            ch=ch)
        assert thresh_tif_path is not None, "threshold {} not found".format(
            thresh_tif_path)
        output_img_path = cic_outspector.cmt_clr_tif_path(
            thresh_dir_path=thresh_dir_path,
            thresh_tif_path=thresh_tif_path)

        overlap_dir_path = cic_outspector.overlap_dir_path(
            case_dir=case_dir,
            ch=ch)
        # note, we can use the original overlap file for coloring
        #  even in the case of roi filter input since original overlap
        #  file will contain more than the overlap info we need
        overlap_path = cic_outspector.cellcount_or_overlap_path(
            overlap_dir_path=overlap_dir_path,
            opairs_section=opairs_section,
            ch=ch,
            gcs=gcs,
            ant='ret' not in overlap_dir_path)  # TODO: less hacky
        assert overlap_path is not None, "overlap {} not found".format(
            overlap_path)
        if verbose:
            print("opened overlap {}".format(overlap_path))
        atlas_tif_path = cic_outspector.atlas_tif_path(
            lvl=lvl,
            annotated_atlas=False)
        assert atlas_tif_path is not None, "atlas tif {} not found".format(
            atlas_tif_path)
        if verbose:
            print("opened atlas {}".format(atlas_tif_path))
        # use communities defined in input_csv_path to color threshold in
        #  thresh_tif_path at regions overlapped in overlap_path
        if gcs != 'roi':
            gcs = int(gcs)
        cmt_clr_thresh_img = cic_outspector.cmt_clr_thresh(
            cons_cmt_csv_path=input_csv_path,
            thresh_tif_path=thresh_tif_path,
            overlap_path=overlap_path,
            atlas_tif_path=atlas_tif_path,
            gcs=gcs,
            lvl=int(lvl),
            hemi='r',
            inj_site_clr_map=inj_site_clr_map,
            verbose=verbose)

        if verbose:
            print("writing {}".format(output_img_path))
        cv2.imwrite(output_img_path, cmt_clr_thresh_img)

        # write additional image since
        #  degenerate retrograde image is difficult to see
        #  and both antero and retro difficult to ascertain location on atlas
        visual_path = cic_outspector.visual_path(
                thresh_dir_path=thresh_dir_path,
                thresh_tif_path=output_img_path)
        grid_ref_tif_path = cic_outspector.grid_ref_tif_path(
            overlap_path=overlap_path, ch=ch)
        # if annotated atlas argument specified, overlay over that
        if annotated_atlas:
            grid_ref_tif_path = cic_outspector.atlas_tif_path(
                lvl=lvl,
                annotated_atlas=True)

        assert os.path.isfile(grid_ref_tif_path), \
            "No grid reference tif found {}".format(grid_ref_tif_path)
        if verbose:
            print("calculating, writing visual image {}".format(visual_path))
        visual_img = cic_plot.visual_img(
            grid_ref_tif_path=grid_ref_tif_path,
            output_img_path=output_img_path,
            to_erode_compose_img=cmt_clr_thresh_img,
            verbose=verbose)

        cv2.imwrite(visual_path, visual_img)

        output_pickle_path = cic_utils.pickle_path(output_img_path)
        pickle.dump(args, open(output_pickle_path, "wb"))
        if verbose:
            print("Wrote pickle args to {}".format(output_pickle_path))


if __name__ == "__main__":
    main()
