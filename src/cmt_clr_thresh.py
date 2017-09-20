#!/usr/bin/env python
import argparse
import os
import cic_outspector
import sys
import cv2


def main():
    parser = argparse.ArgumentParser(description='Creates an atlas matching '
                                     'series of threshold images with '
                                     'labelling colored by community')
    parser.add_argument('-i', '--input_csv',
                        help='Path to CSV containing consensus community '
                        'structure ',
                        required=True)
    parser.add_argument('-cd', '--case_dir',
                        help='Directory to Connection Lens casse',
                        required=True)
    parser.add_argument('-gcs', '--grid_cell_size',
                        required=True)
    parser.add_argument('-lvl', '--atlas_level',
                        help='Atlas level to write',
                        required=True)
    parser.add_argument('-ch', '--channel',
                        help='Case channel to write to output',
                        required=True)
    parser.add_argument('-o', '--output_img_path',
                        help='Output path of Tiff containing community colored'
                        ' threshold labelling',
                        required=True)
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
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
    output_img_path = args['output_img_path']

    gcs = args['grid_cell_size']
    lvl = args['atlas_level']
    verbose = args['verbose']

    # get section from opairs.lst
    opairs_section = cic_outspector.opairs_section(case_dir=case_dir,
                                                   lvl=lvl)

    # check that we have section for ARA level, if not exit WITHOUT error
    #  idea is that we can call this from levels 1 - 132
    if opairs_section is None:
        if verbose:
            print("No opairs.lst section found for ARA level {}".format(lvl))
        sys.exit(0)
    # else have opairs section now get threshold tif
    else:
        thresh_dir_path = cic_outspector.thresh_dir_path(
            case_dir=case_dir,
            ch=ch)
        thresh_tif_path = cic_outspector.thresh_tif_path(
            thresh_dir_path=thresh_dir_path,
            opairs_section=opairs_section,
            ch=ch)
        assert thresh_tif_path is not None, "threshold {} not found".format(
            thresh_tif_path)

        overlap_dir_path = cic_outspector.overlap_dir_path(
            case_dir=case_dir,
            ch=ch)
        overlap_path = cic_outspector.overlap_path(
            overlap_dir_path=overlap_dir_path,
            opairs_section=opairs_section,
            ch=ch,
            gcs=gcs)
        assert overlap_path is not None, "overlap {} not found".format(
            overlap_path)
        atlas_tif_path = cic_outspector.atlas_tif_path(lvl=lvl)
        assert atlas_tif_path is not None, "atlas tif {} not found".format(
            atlas_tif_path)
        # user communities defined in input_csv_path to color threshold in
        #  thresh_tif_path at regions overlapped in overlap_path
        cmt_clr_thresh_img = cic_outspector.cmt_clr_thresh(
            char_cmt_csv_path=input_csv_path,
            thresh_tif_path=thresh_tif_path,
            overlap_path=overlap_path,
            atlas_tif_path=atlas_tif_path,
            gcs=gcs,
            lvl=lvl,
            hemi='r')
        cv2.imwrite(output_img_path, cmt_clr_thresh_img)


if __name__ == "__main__":
    main()
