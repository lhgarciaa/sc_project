#!/usr/bin/env python
from __future__ import print_function
import argparse
from cic_dis import cic_utils
from cic_dis import cic_plot
from cic_dis import cic_overlap
from cic_dis import cic_outspector
import time
import plotly.plotly as py
import plotly.graph_objs as go
from collections import defaultdict
import os
import cv2
import cPickle as pickle


def main():
    parser = argparse.ArgumentParser(description="Render stacked community"
                                     " connectivity matrix")
    parser.add_argument('-cmc', '--ctx_mat_csv',
                        help='Input, labeled row source, column destination '
                        'annotation CSV',
                        required=True)
    parser.add_argument('-ccsc', '--char_com_str_csv',
                        help='Path to CSV containing consensus community '
                        'structure ',
                        required=True)
    parser.add_argument('-aoc', '--agg_overlap_csv',
                        help='Input aggregated overlap csv',
                        required=True)
    parser.add_argument('-lvls', '--levels',
                        help='List of levels to visualize',
                        required=True,
                        nargs='+')
    parser.add_argument('-vimgs', '--visual_images',
                        help='List of images for visualizing split ROIs',
                        nargs='+')
    parser.add_argument('-iso', '--injection_site_order',
                        help='Order list for injection sites e.g. {}'.format(
                            '-iso BLA_am BLA_al BLA_ac'),
                        nargs='+',
                        default=[])
    parser.add_argument('-srs', '--split_rois',
                        help="List of ROIs to split into quadrants, can specify mode with e.g. 'ACB:mdlvl', if no mode specified then 'quad' is default",  # noqa
                        nargs='+',
                        default=[])
    parser.add_argument('-fcs', '--focus_roi',
                        help='ROI to plot exclusively')
    parser.add_argument('-gcs', '--grid_cell_size',
                        help='Grid cell size to use for visual image',
                        default=175,
                        required=False)
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
                        action='store_true')

    args = parser.parse_args()
    ctx_mat_csv = args.ctx_mat_csv
    char_com_str_csv = args.char_com_str_csv
    agg_overlap_csv = args.agg_overlap_csv
    levels = args.levels
    verbose = args.verbose
    injection_site_order = args.injection_site_order
    split_rois = args.split_rois
    # create dct for roi mode lookup later
    roi_mode_dct = {}
    for roi_mode in split_rois:
        roi_mode_lst = roi_mode.split(':')
        if len(roi_mode_lst) > 1:
            roi_mode_dct[roi_mode_lst[0]] = roi_mode_lst[1]
        else:
            roi_mode_dct[roi_mode_lst[0]] = 'quad'  # quad is default
    focus_roi = args.focus_roi
    visual_images = args.visual_images
    grid_cell_size = args.grid_cell_size

    # what we want to do here:
    #  1) Open all the freakin CSVs
    #  2) Create a DICT from community to roi list of rois with overlap amount
    #     { lvl: { cmt_idx : { roi : ovlp } } }
    #  3) Plot DICT as a bar chart or matrix or something

    # 1) opening all the freakin CSVs
    # OPEN CONNECTIVITY MATRIX
    if verbose:
        print("Opening ctx matrix from {}...".format(ctx_mat_csv))
        start = time.time()
    (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) = \
        cic_utils.read_ctx_mat(ctx_mat_csv)
    # check for capitlization/duplicates
    cic_utils.dup_check_container(dup_check_roi_container=row_roi_name_npa,
                                  input_csv_path=ctx_mat_csv)

    cic_utils.dup_check_container(dup_check_roi_container=col_roi_name_npa,
                                  input_csv_path=ctx_mat_csv)
    if verbose:
        print("opened ctx matrix in {:.04}s".format(time.time() - start))
        print("(num rows, num cols) {}".format(ctx_mat_npa.shape))
        print("top left val {}".format(ctx_mat_npa[0][0]))

    # OPEN CHAR COMMUNITY STRUCTURE
    if verbose:
        print("Opening char com str csv {}...".format(char_com_str_csv))
        start = time.time()
    cons_cmt_str = cic_plot.cons_cmt_str(
        cons_cmt_csv_path=char_com_str_csv,
        inj_site_order_lst=injection_site_order)
    if verbose:
        print("opened char com str csv in {:.04}s".format(time.time() - start))
        print("num communities {}".format(len(cons_cmt_str)))

    # OPEN AGG OVERLAP CSV
    if verbose:
        print("Opening aggregated overlap csv {}...".format(agg_overlap_csv))
        start = time.time()
    (agg_overlap_csv_header, agg_overlap_rows) = \
        cic_overlap.read_agg_overlap_csv(input_csv_path=agg_overlap_csv)
    if verbose:
        print("opened agg overlap csv in {:.04}s".format(time.time() - start))
        print("num rows {}".format(len(agg_overlap_rows)))

    # 2) Creating a DICT {cmt : frozenset([roi])}
    max_cmt_idx = -1
    if verbose:
        print("Creating community -> roi dictionary for levels {}...".
              format(levels))
        start = time.time()

    # first populate split roi dct
    lvl_split_roi_dct = {}  # { lvl: { roi: { min_col: ..., max_col,... } } }
    for idx, grid_tup_str in enumerate(col_roi_name_npa):
        if cic_plot.in_lvl_lst(grid_tup_str=grid_tup_str,
                               lvl_lst=levels):
            (lvl, hemi, col_str, row_str) = \
                cic_plot.grid_tup_str_to_lvl_hemi_col_row(grid_tup_str)
            col = int(col_str)
            row = int(row_str)
            # populate split_roi_dct either default, of from lvl
            # get roi and check if it is in the split_rois list
            unsplit_roi_str = cic_plot.col_val(
                col_hdr_str='REGION(S)',
                agg_overlap_csv_header=agg_overlap_csv_header,
                agg_overlap_csv_rows=agg_overlap_rows,
                grid_tup_str=grid_tup_str)

            # now we need to populate split dict

            if lvl not in lvl_split_roi_dct:
                # { roi: { min_col: ..., max_col,... } }
                split_roi_dct = {}  # create empty dct on every lvl by default
                if verbose:
                    print("populating split roi dct vals, level {}...".format(
                        lvl))
            else:
                split_roi_dct = lvl_split_roi_dct[lvl]

            roi_str = cic_plot.in_roi_lst(
                unsplit_roi_str=unsplit_roi_str,
                roi_str_lst=[x.split(':')[0] for x in split_rois])

            if (roi_str is not None and
                    (focus_roi is None or focus_roi in roi_str)):
                if roi_str not in split_roi_dct:
                    roi_dct = {'min_col': col,
                               'max_col': col,
                               'min_row': row,
                               'max_row': row,
                               'mode': roi_mode_dct[roi_str]}
                    if verbose:
                        print("populating {} split {} vals".format(
                            roi_str, roi_mode_dct[roi_str]))
                else:
                    roi_dct = split_roi_dct[roi_str]

                # update split_roi_dct
                roi_dct['min_col'] = min(roi_dct['min_col'], col)
                roi_dct['max_col'] = max(roi_dct['max_col'], col)
                roi_dct['min_row'] = min(roi_dct['min_row'], row)
                roi_dct['max_row'] = max(roi_dct['max_row'], row)
                split_roi_dct[roi_str] = roi_dct
            lvl_split_roi_dct[lvl] = split_roi_dct

    # now check if visual images list specified, and if so then write out imgs
    if visual_images is not None:
        assert len(visual_images) == len(levels)  # must be one image per lvl
        for lvl_idx, lvl in enumerate(levels):
            img_path = visual_images[lvl_idx]
            assert lvl in img_path, "level {} not in {}... \nvisual image order {} does not match order level order {}".format(lvl, img_path, visual_images, levels)  # noqa
            assert os.path.isfile(img_path)
            if verbose:
                start = time.time()
                print("Making split roi image with {} and gcs {}...".format(
                    img_path, grid_cell_size))
            split_roi_atlas_img = cic_outspector.make_split_roi_atlas_img(
                ann_atlas_tif_path=img_path,
                gcs=grid_cell_size,
                lvl=lvl,
                split_roi_dct=lvl_split_roi_dct[lvl],
                hemi='r',
                agg_overlap_csv_header=agg_overlap_csv_header,
                agg_overlap_csv_rows=agg_overlap_rows,
                verbose=verbose)

            split_roi_atlas_img_path = \
                cic_outspector.split_roi_atlas_img_path(
                    out_dir_path=os.path.dirname(img_path),
                    atlas_tif_path=img_path,
                    split_rois=split_rois,
                    focus_roi=focus_roi)

            cv2.imwrite(split_roi_atlas_img_path, split_roi_atlas_img)
            if verbose:
                print("done making split roi image in {:.04}s".format(
                    time.time() - start))

    # walk through each non-zero entry of ctx mat csv, get roi and bin by cmt
    lvl_cmt_dct = {}  # { lvl : cmt_roi_dct }
    for idx, grid_tup_str in enumerate(col_roi_name_npa):
        if cic_plot.in_lvl_lst(grid_tup_str=grid_tup_str,
                               lvl_lst=levels):
            lvl = cic_plot.grid_tup_str_to_lvl_hemi_col_row(grid_tup_str)[0]
            if lvl not in lvl_cmt_dct:
                print("populating roi overlap values, level {}...".format(lvl))
            # { lvl : { cmt_idx { roi : ovlp } } }
            cmt_roi_dct = lvl_cmt_dct.get(lvl, {})
            cmt_idx = cic_plot.cmt_idx_from_grid_tup_str(
                cons_cmt_str=cons_cmt_str,
                grid_tup_str=grid_tup_str)
            assert cmt_idx is not None
            max_cmt_idx = max(max_cmt_idx, cmt_idx)
            unsplit_roi_str = cic_plot.col_val(
                col_hdr_str='REGION(S)',
                agg_overlap_csv_header=agg_overlap_csv_header,
                agg_overlap_csv_rows=agg_overlap_rows,
                grid_tup_str=grid_tup_str)
            assert unsplit_roi_str is not None
            if focus_roi is None or focus_roi in unsplit_roi_str:
                # split rois if they are in lvl_split_roi_dct
                roi_str = cic_plot.split_roi(
                    unsplit_roi_str=unsplit_roi_str,
                    grid_tup_str=grid_tup_str,
                    split_roi_dct=lvl_split_roi_dct[lvl])
                # update overlap value in roi overlap dictionary for this level
                roi_ovlp_dct = cmt_roi_dct.get(cmt_idx, {})
                inj_site = cic_plot.col_val(
                    col_hdr_str='Injection Site',
                    agg_overlap_csv_header=agg_overlap_csv_header,
                    agg_overlap_csv_rows=agg_overlap_rows,
                    grid_tup_str=grid_tup_str)
                assert inj_site is not None
                row_idx = row_roi_name_npa.tolist().index(inj_site)

                # do a few sanity checks before setting roi_ovlp_dct val
                grid_only_str = cic_plot.col_val(
                    col_hdr_str='GRID ONLY',
                    agg_overlap_csv_header=agg_overlap_csv_header,
                    agg_overlap_csv_rows=agg_overlap_rows,
                    grid_tup_str=grid_tup_str)
                overlap_str = cic_plot.col_val(
                    col_hdr_str='OVERLAP',
                    agg_overlap_csv_header=agg_overlap_csv_header,
                    agg_overlap_csv_rows=agg_overlap_rows,
                    grid_tup_str=grid_tup_str)
                grid_only = float(grid_only_str)
                overlap = int(overlap_str)
                fraction_overlap = overlap / (grid_only + overlap)
                assert ctx_mat_npa[row_idx][idx] == fraction_overlap, \
                    "({}, {}) ctx mat overlap {} does not equal {} agg overlap {}".format(row_idx, idx, ctx_mat_npa[row_idx][idx], grid_tup_str, fraction_overlap)  # noqa
                # use regular overlap pixel count since more intuitive
                roi_ovlp_dct[roi_str] = \
                    roi_ovlp_dct.get(roi_str, 0) + overlap

                # point to all the potentially new dict vals
                cmt_roi_dct[cmt_idx] = roi_ovlp_dct
            lvl_cmt_dct[lvl] = cmt_roi_dct

    if verbose:
        print("Finished creating dict in in {:.04}s".format(
            time.time() - start))
        for lvl in sorted(lvl_cmt_dct):
            print("-- Level {} --".format(lvl))
            cmt_roi_dct = lvl_cmt_dct[lvl]
            print("Num communities {}".format(len(cmt_roi_dct)))
            for cmt_idx in sorted(cmt_roi_dct.keys()):
                roi_ovlp_dct = cmt_roi_dct[cmt_idx]
                print("Community {} roi count {} total ovlp {}".format(
                    injection_site_order[cmt_idx],
                    len(roi_ovlp_dct),
                    sum([roi_ovlp_dct[roi] for
                         roi in roi_ovlp_dct])))

    # 3) Plot DICT as a bar chart or matrix or something
    if verbose:
        print("Plotting a bar chart or matrix or something for {} levels and {} communities...".format(len(lvl_cmt_dct), max_cmt_idx + 1))  # noqa
        start = time.time()

    if verbose:
        print("creating top roi list...")
    # create { cmt : [ [roi], ... ] } list of most projected roi for each cmt
    cmt_top_roi_lst = defaultdict(list)
    for lvl in sorted(lvl_cmt_dct):  # this will sort top ROIs correctly
        cmt_roi_dct = lvl_cmt_dct[lvl]
        # not every level has every community
        for cmt_idx in xrange(max_cmt_idx + 1):
            if cmt_idx in cmt_roi_dct:
                # lst of tups will be sorted by overlap value
                lst = sorted(cmt_roi_dct[cmt_idx].iteritems(),
                             key=lambda (k, v): (v, k), reverse=True)
                roi_str = "len lst {} ".format(len(lst))
                roi_str = "({}) ".format(lst[0][0]).replace("|", " ")
                for tup in lst[1:1]:
                    roi_str += " ({})".format(tup[0]).replace("|", " ")
                    # create list of strings
                cmt_top_roi_lst[cmt_idx].append(roi_str)
            else:
                cmt_top_roi_lst[cmt_idx].append('')

    if verbose:
        print("making traces for each community...")
    # create traces, or levels that will be plotted as bars
    # first create the values
    cmt_trace_y_dct = defaultdict(list)  # { cmt_idx : [ lvl trace val, ...] }
    # populate total overlap per level for normalization
    lvl_trace_total_dct = defaultdict(float)
    for lvl in sorted(lvl_cmt_dct):  # this will sort trace values correctly
        # append number of rois in each community for each cmt
        cmt_roi_dct = lvl_cmt_dct[lvl]
        # not every level has equal num communities, check for that
        for cmt_idx in xrange(max_cmt_idx + 1):
            if cmt_idx in cmt_roi_dct:
                roi_ovlp_dct = cmt_roi_dct[cmt_idx]
                # append num rois to cmt_trace_y_dct
                cmt_trace_y_dct[cmt_idx].append(
                    sum([float(roi_ovlp_dct[roi]) for roi in roi_ovlp_dct]))
                lvl_trace_total_dct[lvl] = \
                    lvl_trace_total_dct[lvl] + \
                    sum([float(roi_ovlp_dct[roi]) for roi in roi_ovlp_dct])
            else:
                cmt_trace_y_dct[cmt_idx].append(0)  # append 0 amount of trace

    if verbose:
        print("normalizing traces to 100% ...")
    # normalize traces to 100 %
    # get community from the first level
    # need to sort this too since cmt_trace_y_dct points to a list
    for lvl_idx, lvl in enumerate(sorted(lvl_cmt_dct)):
        cmt_roi_dct = lvl_cmt_dct[lvl]
        for cmt_idx in sorted(cmt_roi_dct):
            # normalize to 100% using level values
            cmt_trace_y_dct[cmt_idx][lvl_idx] = \
                (float(cmt_trace_y_dct[cmt_idx][lvl_idx]) /
                 lvl_trace_total_dct[lvl]) * 100.0

    if verbose:
        print("populating graph object and writing file...")
    # now populate graph object
    # not all lvels have all communities, so use global max to cover all
    traces = []
    for cmt_idx in xrange(max_cmt_idx + 1):
        traces.append(
            go.Bar(
                # don't forget to sort here bro
                x=["lvl {}".format(x) for x in sorted(lvl_cmt_dct)],
                y=cmt_trace_y_dct[cmt_idx],
                text=cmt_top_roi_lst[cmt_idx],
                textposition='auto',
                name="{} community".format(
                    injection_site_order[cmt_idx]))
        )

    data = traces
    layout = go.Layout(
        barmode='stack',
        width=1500,
        height=1500
    )

    fig = go.Figure(data=data, layout=layout)
    base_agg_overlap_csv = 'stacked-' + os.path.basename(agg_overlap_csv)
    out_img_path = base_agg_overlap_csv.replace(
        '.csv', '-{}.png'.format(levels))
    if focus_roi is not None:
        out_img_path = out_img_path.replace('.png',
                                            '-{}.png'.format(focus_roi))
    py.image.save_as(fig, out_img_path)
    if verbose:
        print("Finished plotting {} in {:.04}s".format(
            out_img_path,
            time.time() - start))

    output_pickle_path = cic_utils.pickle_path(out_img_path)
    pickle.dump(args, open(output_pickle_path, "wb"))
    if verbose:
        print("Wrote pickle args to {}".format(output_pickle_path))


if __name__ == '__main__':
    main()
