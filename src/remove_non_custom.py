
from __future__ import print_function
import argparse
import os
import glob
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="Removes non SC custom files")
    parser.add_argument('-gcs', '--grid_cell_size',
                        help='Grid cell size',
                        required=True)
    parser.add_argument('-rp', '--root_path',
                        help='Directory to search for threshold tifs',
                        required=True)
    parser.add_argument('-v', '--verbose',
                        help='Print status messages',
                        action='store_true')
    parser.add_argument('-dry', '--dry_run',
                        help="Prints files to be deleted",
                        action='store_true')

    # required args, and derivitives
    args = vars(parser.parse_args())

    root_path = args['root_path']
    grid_cell_size = args['grid_cell_size']
    verbose = args['verbose']
    dry_run = args['dry_run']
    possible_levels = ('086', '090', '096', '100')

    tracer_mode = "anterograde" if 'ant' in root_path else "retrograde"

    if verbose:
        "{} tracer mode".format(tracer_mode)

    assert os.path.isdir(root_path), "{} is not a valid path".format(root_path)

    # walk through root dir finding all files matching *-th.tif
    timestamps_to_old_filenames = []
    overlap_not_found_filenames = []
    overlap_malformed_filenames = []
    overlap_not_correct_filenames = []
    overlap_inj_site_none_filenames = []
    files_to_be_deleted = []


    import pdb;

    # FIRST get the length of everything for printing status
    #  check for retrograde first
    total_len = 0
    if tracer_mode == "retrograde":
        if verbose:
            print("Indexing retrograde images")
        tif_wc_ext = '*-degenerate.tif'
        for rootpath, dirnames, filenames in os.walk(root_path):
            th_tif_wildcard = os.path.join(rootpath, tif_wc_ext)
            total_len += len(glob.glob(th_tif_wildcard))

    else:
        # now check for anterograde
        if verbose:
            print("Indexing anterograde images")
        tif_wc_ext = '*-th.tif'
        for rootpath, dirnames, filenames in os.walk(root_path):
            th_tif_wildcard = os.path.join(rootpath, tif_wc_ext)
            total_len += len(glob.glob(th_tif_wildcard))

    if total_len == 0:
        eprint("No threshold files found")
        exit(1)

    tif_ext = tif_wc_ext.replace('*', '')

    # now set the overlap based on if roi or grid based, ant or retrograde
    if grid_cell_size == 'roi':
        if tracer_mode == 'retrograde':
            csv_ext = '_cellcount.csv'
        else:
            csv_ext = '_custom_SC_DIVISIONS_pixelcount.csv'
        if verbose:
            print("Using roi {} overlap file ext {} ".format(tracer_mode,
                                                             csv_ext))
    else:  # grid based
        if tracer_mode == 'anterograde':
            csv_ext = '_grid-{}_pixelcount.csv'.format(grid_cell_size)
        else:  # retrograde
            csv_ext = '_grid-{}_cellcount.csv'.format(grid_cell_size)
        if verbose:
            print("Using grid overlap file ext {}".format(csv_ext))

    for rootpath, dirnames, filenames in os.walk(root_path):
        # first check for retrograde
        th_tif_wildcard = os.path.join(rootpath, tif_wc_ext)
        for thresh_img_path in glob.glob(th_tif_wildcard):
            # example:
            # threshold/channels/2/SW120228-02B_2_01_ch2-th.tif
            # overlap/2/SW120228-02B_2_01_ch2_grid-175_pixelcount.csv
            overlap_wildcard = thresh_img_path.replace(
                'threshold/channels', 'overlap')
            overlap_path = overlap_wildcard.replace(
                tif_ext,
                csv_ext)
            assert os.path.isfile(overlap_path)
            custom_wildcard = overlap_path.replace(
                csv_ext, "_SC_DIVISIONS_*_pixelcount.tif")

            SC_custom_path = glob.glob(custom_wildcard)
            if len(SC_custom_path) == 0:
                removal_wildcard = overlap_path.replace(csv_ext, "*")
                removal_paths = glob.glob(removal_wildcard)
                # print("These are removal paths: ", removal_paths)
                # print("What is this lenght: ", len())
                assert len(removal_paths) == 2
                assert overlap_path in removal_paths
                files_to_be_deleted.append(thresh_img_path)
                files_to_be_deleted.extend(removal_paths)
		for rm_path in removal_paths:
		    rm_path = os.path.basename(rm_path)
		    # Make sure removal paths are not from levels of interest
		    assert not any(lvl in rm_path for lvl in possible_levels)
            else:
                assert len(SC_custom_path) == 1
                assert any(lvl in SC_custom_path[0] for lvl in possible_levels)

    if dry_run:
        print("Dry run, would remove these files: ")
        for file_name in files_to_be_deleted:
            print(file_name)
        print("Would remove {} files".format(len(files_to_be_deleted)))
    else:
        print("Removed {} files".format(len(files_to_be_deleted)))
        for file_name in files_to_be_deleted:
            os.remove(file_name)

    # SC_custom_path = glob.glob(overlap_path)
    # assert len(SC_custom_path) == 1, "More than one overlap file found with ext."


if __name__ == '__main__':
    main()
