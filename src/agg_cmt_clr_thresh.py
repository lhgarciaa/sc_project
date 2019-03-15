#!/usr/bin/env python
import argparse
import os
from cic_dis import cic_outspector
from cic_dis import cic_utils
import cv2
import cPickle as pickle
from cic_dis import cic_plot


def main():
    parser = argparse.ArgumentParser(description='Creates an atlas matching '
                                     'series of threshold images with '
                                     'labelling colored by community')
    parser.add_argument('-cb', '--case_basedir',
                        help='Directory of Connection Lens Case base dirs',
                        required=True)
    parser.add_argument('-cct', '--case_ch_tups',
                        help='List of case:ch subdirs from base e.g. -cc SW120228-02B:2 SW130212-02A:2',  # noqa
                        nargs='+')
    parser.add_argument('-gcs', '--grid_cell_size',
                        required=True)
    parser.add_argument('-lvl', '--atlas_level',
                        help='Atlas level to write',
                        required=True)
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
                        action='store_true')
    parser.add_argument('-aa', '--annotated_atlas',
                        help='Overlay over annotated atlas (i.e. with labels)',
                        action='store_true')
    parser.add_argument(
        '-od', '--output_dir',
        help='Directory for aggregated output, should already exist',
        required=True)

    args = vars(parser.parse_args())

    output_dir_path = args['output_dir']
    assert os.path.isdir(output_dir_path), \
        "output dir path {} does not exist".format(output_dir_path)

    gcs = args['grid_cell_size']
    lvl = args['atlas_level']
    verbose = args['verbose']
    annotated_atlas = args['annotated_atlas']

    if verbose:
        print "args {}".format(args)

    # get base dir and case and march through subdirs to aggregate
    case_basedir = args['case_basedir']
    case_ch_tups = args['case_ch_tups']
    append_case_ch_tups = ""  # append new string and then write to args
    for case_ch_tup in case_ch_tups:
        assert ':' in case_ch_tup, "Expected format case:ch instead found {}".\
            format(case_ch_tup)
        case_ch_tup_lst = case_ch_tup.split(':')
        assert len(case_ch_tup_lst) == 2, "wtf is this {}".format(
            case_ch_tup_lst)
        case = case_ch_tup_lst[0]
        ch = case_ch_tup_lst[1]
        case_dir = os.path.join(case_basedir, case)
        assert os.path.isdir(case_dir),\
            "no case dir {}".format(case_dir)
        # get and check that overlap dir path exists
        overlap_ch_dir_path = cic_outspector.overlap_dir_path(
            case_dir=case_dir,
            ch=ch)
        assert os.path.isdir(overlap_ch_dir_path),\
            "no overlap dir {}".format(overlap_ch_dir_path)

        if verbose:
            print "AGGREGATING case {} channel {}".format(case, ch)

        # get section from opairs.lst
        opairs_section = cic_outspector.opairs_section(case_dir=case_dir,
                                                       lvl=lvl)

        # check that we have section for ARA level, if not exit WITHOUT error
        #  idea is that we can callv this from levels 1 - 132
        if opairs_section is None:
            if verbose:
                print("No opairs.lst section found for ARA level {}".format(
                    lvl))
                print("skipping without error")
        # else have opairs section now get threshold tif
        else:
            thresh_dir_path = cic_outspector.thresh_dir_path(
                case_dir=case_dir,
                ch=ch)
            thresh_tif_path = cic_outspector.roi_filter_or_thresh_tif_path(
                thresh_dir_path=thresh_dir_path,
                opairs_section=opairs_section,
                ch=ch)
            assert thresh_tif_path is not None, \
                "threshold {} not found".format(thresh_tif_path)
            cmt_clr_tif_path = cic_outspector.cmt_clr_tif_path(
                thresh_dir_path=thresh_dir_path,
                thresh_tif_path=thresh_tif_path)
            assert cmt_clr_tif_path is not None, \
                "cmt_clr_tif_path {} not found".format(cmt_clr_tif_path)

            agg_cmt_clr_tif_path = cic_outspector.agg_cmt_clr_tif_path(
                cmt_clr_tif_path=cmt_clr_tif_path,
                output_dir_path=output_dir_path,
                lvl=lvl)

            if verbose:
                desc_str = "does not exist, will create"
                if os.path.exists(agg_cmt_clr_tif_path):
                    desc_str = "exists, will compose"
                print("{} {}".format(agg_cmt_clr_tif_path, desc_str))

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
                ant='ret' not in overlap_dir_path)  # TODO: less hacky here
            assert overlap_path is not None, "overlap {} not found".format(
                overlap_path)

            if gcs != 'roi':
                gcs = int(gcs)
            cmt_clr_thresh_img = cic_outspector.agg_cmt_clr_thresh(
                cmt_clr_tif_path=cmt_clr_tif_path,
                agg_cmt_clr_tif_path=agg_cmt_clr_tif_path,
                gcs=gcs,
                lvl=int(lvl),
                hemi='r',
                verbose=verbose)

            if verbose:
                print("writing {}".format(agg_cmt_clr_tif_path))
            cv2.imwrite(agg_cmt_clr_tif_path, cmt_clr_thresh_img)

            # write additional image since
            #  degenerate retrograde image is difficult to see
            #  and both antero and retro difficult to observe location on atlas
            #  use output dir path as thresh dir path since that's where visual
            #   image should go
            visual_path = cic_outspector.visual_path(
                    thresh_dir_path=output_dir_path,
                    thresh_tif_path=agg_cmt_clr_tif_path)
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
                print(
                    "calculating, writing visual image from {} and {} to {}".
                    format(
                        grid_ref_tif_path,
                        agg_cmt_clr_tif_path,
                        visual_path))
            visual_img = cic_plot.visual_img(
                grid_ref_tif_path=grid_ref_tif_path,
                output_img_path=agg_cmt_clr_tif_path,
                to_erode_compose_img=cmt_clr_thresh_img,
                verbose=verbose)
            cv2.imwrite(visual_path, visual_img)

            append_case_ch_tups += "{}:{} ".format(case, ch)
            args['case_ch_tups'] = append_case_ch_tups

            output_pickle_path = cic_utils.pickle_path(agg_cmt_clr_tif_path)
            pickle.dump(args, open(output_pickle_path, "wb"))
            if verbose:
                print("Wrote pickle args to {}".format(output_pickle_path))


if __name__ == "__main__":
    main()
