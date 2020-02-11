#!/usr/bin/env python
from __future__ import print_function
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import csv
from cic_dis import cic_utils
import cPickle as pickle

# Replacement names for default ROI names
ROI_NAMES = {
    'SCzo_div1': 'SC.m-zo',
    'SCsg_div1': 'SC.m-sg',
    'SCop_div1': 'SC.m-op',
    'SCig_div1': 'SC.m-ig',
    'SCiw_div1': 'SC.m-iw',
    'SCdg_div1': 'SC.m-dg',
    'SCdw_div1': 'SC.m-dw',
    'SCzo_div2': 'SC.cm-zo',
    'SCsg_div2': 'SC.cm-sg',
    'SCop_div2': 'SC.cm-op',
    'SCig_div2': 'SC.cm-ig',
    'SCiw_div2': 'SC.cm-iw',
    'SCdg_div2': 'SC.cm-dg',
    'SCdw_div2': 'SC.cm-dw',
    'SCzo_div3': 'SC.cl-zo',
    'SCsg_div3': 'SC.cl-sg',
    'SCop_div3': 'SC.cl-op',
    'SCig_div3': 'SC.cl-ig',
    'SCiw_div3': 'SC.cl-iw',
    'SCdg_div3': 'SC.cl-dg',
    'SCdw_div3': 'SC.cl-dw',
    'SCig_div4': 'SC.l-ig',
    'SCiw_div4': 'SC.l-iw',
    'SCdg_div4': 'SC.l-dg',
    'SCdw_div4': 'SC.l-dw'
}

# Custom COL order provided by Nora for columns
COL_ORDER = ['SC.m-zo', 'SC.m-sg', 'SC.m-op', 'SC.m-ig', 'SC.m-iw', 'SC.m-dg',
             'SC.m-dw', 'SC.cm-zo', 'SC.cm-sg', 'SC.cm-op', 'SC.cm-ig',
             'SC.cm-iw', 'SC.cm-dg', 'SC.cm-dw', 'SC.cl-zo', 'SC.cl-sg',
             'SC.cl-op', 'SC.cl-ig', 'SC.cl-iw', 'SC.cl-dg', 'SC.cl-dw',
             'SC.l-ig', 'SC.l-iw', 'SC.l-dg', 'SC.l-dw']

# Custom ROW order provided by Nora for group SC-assoc-stacked_bar_ant
ROW_ORDER_1 = ["RSPv_interm", "RSPv_caudal", "RSPd_rostral", "RSPagl",
               "PTLp_lat", "RSPd_caudal", "ACAv_interm", "TEa_caudal",
               "ACAv_caudal", "PTLp_med", "ACAd_interm", "ACAv_rostral",
               "RSPv_rostral", "ACAd_rostral", "ACAd_caudal", "ORBm", "PL",
               "ILA", "TEa_rostral", "ORBvl", "ORBl"]

# Custom ROW order provided by Nora for group SC SC-sensory-stacked-bar-ant
ROW_ORDER_2 = ["VISp_caudal", "VISp_caudomed", "VISp_rostromed", "VISal",
               "VISam", "AUDp_interm", "AUDd", "MOs_medial", "SSp_tr",
               "MOs_caudal", "MOs_lateral", "SSp_bfd", "MOp-bfd", "MOp-oro",
               "MOs_rostral", "MOp-tr", "SSp_ll", "SSp_m", "SSp_n", "SSp_ul",
               "SSs"]

# COLORS used for each subsection
COLORS = ('#990000', '#FF6600', '#116600', '#660078')
NAMES = ('SC.m', 'SC.cm', 'SC.cl', 'SC.l')


def main():
    parser = argparse.ArgumentParser(
        description="Creates matrix table from connectivity matrix, "
                    "no communities")

    parser.add_argument('-m', '--matrix_csv',
                        help='Row/column based connectivity matrix',
                        required=True)

    parser.add_argument('-v', '--verbose',
                        help='Print matrix, cluster related output',
                        action='store_true')

    parser.add_argument('-fmt', '--format',
                        help='Format of plot (e.g. svg, png,...)',
                        default='svg')

    parser.add_argument('-fs', '--fontsize',
                        help='Font size of tick labels in x and y',
                        type=int,
                        default=6)

    parser.add_argument('-rn', '--roi_replacement',
                        help='Replaces default roi names with ROI_NAMES',
                        action='store_true')

    parser.add_argument('-rc', '--reorder_column',
                        help='Replaces default roi names with ROI_NAMES',
                        action='store_true')

    parser.add_argument('-rr', '--reorder_row',
                        help='Replaces default roi names with ROI_NAMES',
                        action='store_true')

    parser.add_argument('-ns', '--no_shading',
                        help='Table with no shading, only values ',
                        action='store_true')

    parser.add_argument('-p', '--percentage',
                        help='Creates table with percentage values',
                        action='store_true')

    parser.add_argument('-l', '--legend',
                        help='Adds colorbar next to figure',
                        action='store_true')

    parser.add_argument('-csv', '--output_csv',
                        help='Outputs a csv, instead of a figure',
                        action='store_true')

    args = vars(parser.parse_args())

    matrix_csv_path = args['matrix_csv']
    assert os.path.isfile(matrix_csv_path),\
        "Can't find row column matrix csv file {}".format(matrix_csv_path)

    # PARSE ARGUMENTS
    verbose = args['verbose']
    fontsize = args['fontsize']
    roi_replacement = args['roi_replacement']
    reorder_column = args['reorder_column']
    reorder_row = args['reorder_row']
    no_shading = args['no_shading']
    percentage = args['percentage']
    legend = args['legend']
    output_csv = args['output_csv']
    fmt = "{}".format(args['format'])
    output_dir, base_name = os.path.split(matrix_csv_path)
    chart_type = "_table"

    if no_shading:
        chart_type += "_no_shading"
    if percentage:
        chart_type += "_percentage"

    graph_name = base_name.replace(
        '.csv',
        '{}.{}'.format(chart_type, fmt))

    out_path = os.path.join(output_dir, graph_name)

    # Open, read input matrix csv
    (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) = \
        cic_utils.read_ctx_mat(matrix_csv_path)

    if roi_replacement:
        # Replace roi names with custom ROI_NAMES
        col_roi_name_npa = np.array(
            [ROI_NAMES[roi] for roi in col_roi_name_npa])

    if verbose:
        print("Read row ROIs: \n{}\n".format(row_roi_name_npa))
        print("Read col ROIs: \n{}\n".format(col_roi_name_npa))

    # Create in case no changes are needed
    new_col_roi_indices = np.arange(len(col_roi_name_npa))
    new_row_roi_indices = np.arange(len(row_roi_name_npa))

    # Reordering columns
    if reorder_column:
        new_col_roi_indices = []
        col_order_dict = dict(
            [(roi, indx) for indx, roi in enumerate(col_roi_name_npa)])

        for roi in COL_ORDER:
            if roi in col_roi_name_npa:
                new_col_roi_indices.append(col_order_dict[roi])

    # Reordering rows
    if reorder_row:
        new_row_roi_indices = []
        row_order_dict = dict(
            [(roi, indx) for indx, roi in enumerate(row_roi_name_npa)])

        # Determine what row order to use
        if 'assoc' in matrix_csv_path:
            row_order = ROW_ORDER_1
        else:
            row_order = ROW_ORDER_2

        for roi in row_order:
            if roi in row_roi_name_npa:
                new_row_roi_indices.append(row_order_dict[roi])

    # Reorder ctx matrix npa
    new_col_roi_name_npa = np.array(col_roi_name_npa[new_col_roi_indices])
    new_row_roi_name_npa = np.array(row_roi_name_npa[new_row_roi_indices])
    temp_rs = ctx_mat_npa[new_row_roi_indices, :]
    reorder_ctx_mat_npa = temp_rs[:, new_col_roi_indices]

    if percentage:
        for i in range(len(new_row_roi_name_npa)):
            row_total = np.sum(reorder_ctx_mat_npa[i])
            reorder_ctx_mat_npa[i] = reorder_ctx_mat_npa[i] / row_total

    if output_csv:
        all_rows = []
        print("col name: ", new_col_roi_name_npa)
        all_rows.append([' '] + list(new_col_roi_name_npa))
        for rowe in range(len(new_row_roi_name_npa)):
            all_rows.append([new_row_roi_name_npa[rowe]] +
                            list(reorder_ctx_mat_npa[rowe]))
        print("row name: ", new_row_roi_name_npa)

        with open(graph_name, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile)

            csvwriter.writerows(all_rows)
        print("Output to {}".format(graph_name))
        return

    # Plot creation
    fig, ax = plt.subplots(figsize=(7.5, 10))

    im = heatmap(ax=ax,
                 ctx_mat_npa=reorder_ctx_mat_npa,
                 row_roi_name_npa=new_row_roi_name_npa,
                 col_roi_name_npa=new_col_roi_name_npa,
                 no_shading=no_shading,
                 fontsize=fontsize,
                 legend=legend)

    annotate_heatmap(im=im,
                     ctx_mat_npa=reorder_ctx_mat_npa,
                     row_roi_name_npa=new_row_roi_name_npa,
                     col_roi_name_npa=new_col_roi_name_npa,
                     no_shading=no_shading)

    fig.tight_layout()
    plt.savefig(out_path, dpi=600)
    pickle_path = cic_utils.pickle_path(out_path)
    pickle.dump(args, open(pickle_path, "wb"))


def annotate_heatmap(im, ctx_mat_npa, row_roi_name_npa,
                     col_roi_name_npa, no_shading):

    # Loop over data dimensions and create text annotations.
    for i in range(len(row_roi_name_npa)):
        for j in range(len(col_roi_name_npa)):
            value = ctx_mat_npa[i, j]
            color = 'black' if value < 0.6 or no_shading else 'w'
            im.axes.text(j, i, round(value, 4),
                         ha="center", va="center", color=color,
                         rotation=90, fontsize=6)


def heatmap(ax, ctx_mat_npa, row_roi_name_npa,
            col_roi_name_npa, no_shading, fontsize, legend):

    if no_shading:
        reorder_ctx_mat_npa_zeros = np.zeros(
            (len(row_roi_name_npa), len(col_roi_name_npa)))
        im = ax.imshow(reorder_ctx_mat_npa_zeros,
                       cmap=plt.cm.gray_r,
                       aspect='auto',
                       vmin=0,
                       vmax=1)
    else:
        im = ax.imshow(ctx_mat_npa,
                       cmap=plt.cm.gray_r,
                       aspect='auto',
                       vmin=0,
                       vmax=1)

    # Create colorbar
    if legend:
        cbar = ax.figure.colorbar(im, ax=ax,)
        # cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
        cbar.ax.set_ylabel("", rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(col_roi_name_npa)))
    ax.set_yticks(np.arange(len(row_roi_name_npa)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(col_roi_name_npa, fontsize=fontsize)
    ax.set_yticklabels(row_roi_name_npa, fontsize=fontsize)

    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5)

    ax.set_xticks(np.arange(ctx_mat_npa.shape[1] + 1) - .5,
                  minor=True)
    ax.set_yticks(np.arange(ctx_mat_npa.shape[0] + 1) - .5,
                  minor=True)

    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=90,)

    return im


def reorder_columns_rows():
    pass


if __name__ == '__main__':
    main()
