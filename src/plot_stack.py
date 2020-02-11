from __future__ import print_function
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
from cic_dis import cic_utils
# import cPickle as pickle

COLORS = ('#990000', '#FF6600', '#116600', '#660078')

NAMES = ('SC.m', 'SC.cm', 'SC.cl', 'SC.l')

# Custom labels provided by Nora for SC-assoc-stacked_bar_ant group
SC_ASSOC_LABELS = ["RSPv_interm", "RSPv_caudal", "RSPd_rostral", "RSPagl",
                   "RSPd_caudal", "PTLp_lat", "TEa_caudal", "ACAv_caudal",
                   "ACAv_interm", "ACAv_rostral", "PTLp_med", "RSPv_rostral",
                   "ACAd_interm", "ACAd_caudal", "ACAd_rostral", "TEa_rostral",
                   "ORBm", "PL", "ILA", "ORBvl", "ORBl"]

# Custom labels provided by Nora for SC-sensory-stacked_bar-ant group
SC_SENSO_LABELS = ["VISp_caudal", "VISp_caudomed", "VISp_rostromed", "VISal",
                   "VISam", "AUDp_interm", "AUDd", "MOs_medial", "SSp_tr",
                   "MOs_caudal", "MOs_lateral", "SSp_bfd", "MOp-bfd",
                   "MOp-oro", "MOs_rostral", "MOp-tr", "SSp_ll", "SSp_m",
                   "SSp_n", "SSp_ul", "SSs"]


def main():
    parser = argparse.ArgumentParser(
        description="Creates stacked bar graphs using row/column"
                    " connectity matrix")

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
                        default=2)

    parser.add_argument('-ct', '--chart_type',
                        help='Type of chart to generate: single,'
                        'levels, ',
                        choices=['single', 'multi_prop', 'levels'],
                        default='single')

    parser.add_argument('-vt', '--value_type',
                        help='Type of value being used, raw_pixel, proportion'
                             'for y axis labeling',
                        choices=['raw_pixel', 'proportion'])

    parser.add_argument('-inj', '--injection_site',
                        help='Injection site of interest to graph e.g., ACAv, '
                             'RSPv, RSPd, can take in comma seperated list',
                        default='all')

    args = vars(parser.parse_args())

    matrix_csv_path = args['matrix_csv']
    assert os.path.isfile(matrix_csv_path),\
        "Can't find row column matrix csv file {}".format(matrix_csv_path)

    #PARSE ARGUMENTS
    verbose = args['verbose']
    fontsize = args['fontsize']
    fmt = "{}".format(args['format'])
    chart_type = args['chart_type']
    value_type = args['value_type']
    injection_site = args['injection_site']
    output_dir, base_name = os.path.split(matrix_csv_path)
    out_path = ''

    if injection_site is not 'all':
        site_lst = injection_site.split(',')

    # Open, read input csv
    (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) = \
        cic_utils.read_ctx_mat(matrix_csv_path)

    if verbose:
        print("Read row ROIs: \n{}\n".format(row_roi_name_npa))
        print("Read col ROIs: \n{}\n".format(col_roi_name_npa))

    # If user provided injection_sites, assert that sites are valid
    if injection_site is not 'all':
        for site in site_lst:
            pass
            assert site in row_roi_name_npa, \
                "{} is not in row roi list...\n{}".format(site,
                                                          row_roi_name_npa)
    else:
        site_lst = row_roi_name_npa

    roi_dict = {}

    # for all the sites in site_lst, get values
    for site in range(len(site_lst)):
        # division level dictionary
        div_level_dict = {}

        site_idx = list(row_roi_name_npa).index(site_lst[site])
        site_vals = ctx_mat_npa[site_idx]
        # Place site for a specific inj site in dictionary
        for idx, value in enumerate(site_vals):
            div_level = col_roi_name_npa[idx]
            div_level_dict[div_level] = value

        graph_name = base_name.replace(
            '.csv',
            '_stacked_{}_{}.{}'.format(chart_type,
                                       value_type,
                                       fmt))

        out_path = os.path.join(output_dir, graph_name)

        if chart_type == 'levels':
            generate_levels_chart(div_level_dict,
                                  site_lst[site],
                                  out_path,
                                  value_type,
                                  COLORS)
        elif chart_type == 'multi_prop':
            roi_values = get_div_proportional_values(div_level_dict)
            roi_dict[site_lst[site]] = roi_values
        else:
            generate_single_chart(div_level_dict,
                                  site_lst[site],
                                  out_path,
                                  COLORS)

    if chart_type == 'multi_prop':
        graph_name = base_name.replace(
            '.csv',
            '_stacked_{}_{}.{}'.format(chart_type,
                                       value_type,
                                       fmt))
        out_path = os.path.join(output_dir, graph_name)
        generate_proportion_group_chart(roi_dict, "Unused", out_path, NAMES, COLORS)

    print("Done")


# Generates single stacked bar chart with proportional labeling, aggregates
# div values across all levels
def generate_single_chart(div_lvl_dict, title, out_path, colors):
    lvls = 1
    ind = np.arange(lvls)
    width = 0.25

    div_values = np.zeros(4)

    for site in div_lvl_dict:
        if 'SC.m' in site:
            div_values[0] += div_lvl_dict[site]
        elif 'SC.cm' in site:
            div_values[1] += div_lvl_dict[site]
        elif 'SC.cl' in site:
            div_values[2] += div_lvl_dict[site]
        else:
            div_values[3] += div_lvl_dict[site]

    div_values = np.split(div_values, 4)
    col_totals = np.sum(div_values, axis=0)
    div_values = np.nan_to_num(div_values / col_totals) * 100

    bars = []
    bottoms = np.zeros(1)
    for idx, division in enumerate(div_values):
        bars.append(plt.bar(
            ind, division, bottom=bottoms, color=colors[idx], width=width))
        bottoms += division

    plt.bar(ind, 0, 1.0, align='center', color='black', label=None)

    plt.xticks(ind, (title,))
    plt.legend((bars[0][0], bars[1][0], bars[2][0], bars[3][0]),
               ('SC.m', 'SC.cm', 'SC.cl', 'SC.l'))

    plt.savefig(out_path, dpi=600)
    plt.close()


def generate_proportion_group_chart(roi_dict, title, out_path, names, colors):
    if 'SC-assoc' in out_path:
        labels = SC_ASSOC_LABELS
    elif 'SC-sensory' in out_path:
        labels = SC_SENSO_LABELS
    else:
        # If not using custom names, simply use key names
        labels = list(roi_dict.keys())

    # data = np.array(list(roi_dict.values()))

    data = np.array([roi_dict[key] for key in labels])
    data_cum = data.cumsum(axis=1)

    fig, ax = plt.subplots(figsize=(7.5, 10))
    ax.invert_yaxis()
    # ax.xaxis.set_visible(False)
    # ax.xaxis.
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(names, colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.8, label=colname, color=color)

    ax.legend(ncol=len(names), bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', mode="expand", fontsize='large')
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels([0, 25, 50, 75, 100])
    plt.yticks(fontsize=15)
    plt.tight_layout()
    plt.margins(0.01)
    plt.savefig(out_path, dpi=600)
    plt.close()


def get_div_proportional_values(div_lvl_dict):
    div_values = np.zeros(4)

    for site in div_lvl_dict:
        if 'SC.m' in site:
            div_values[0] += div_lvl_dict[site]
        elif 'SC.cm' in site:
            div_values[1] += div_lvl_dict[site]
        elif 'SC.cl' in site:
            div_values[2] += div_lvl_dict[site]
        else:
            div_values[3] += div_lvl_dict[site]

    div_values = (div_values / np.sum(div_values)) * 100

    # div_values = np.split(div_values, 4)
    # col_totals = np.sum(div_values, axis=0)
    # div_values = np.nan_to_num(div_values / col_totals) * 100

    return div_values


# Generates 4 stacked bar charts according to ARA level, raw pixel or rational
def generate_levels_chart(div_lvl_dict, title, out_path, value_type, colors):
    lvls = 4  # indentation
    ind = np.arange(lvls)  # the locations for the groups
    width = 0.35  # the width of the bars
    div_lists = [[], [], [], []]

    # Place site in appropriate div list
    for site in div_lvl_dict:
        if 'SC.m' in site:
            div_lists[0].append((site, div_lvl_dict[site]))
        elif 'SC.cm' in site:
            div_lists[1].append((site, div_lvl_dict[site]))
        elif 'SC.cl' in site:
            div_lists[2].append((site, div_lvl_dict[site]))
        else:
            div_lists[3].append((site, div_lvl_dict[site]))

    # Sort div lists by ARA level, 86, 90, 96, 100, for SC charts
    div_lists[0] = [tup[1] for tup in sorted(
        div_lists[0], key=lambda x: int(x[0].split('_')[1]))]
    div_lists[1] = [tup[1] for tup in sorted(
        div_lists[1], key=lambda x: int(x[0].split('_')[1]))]
    div_lists[2] = [tup[1] for tup in sorted(
        div_lists[2], key=lambda x: int(x[0].split('_')[1]))]
    div_lists[3] = [tup[1] for tup in sorted(
        div_lists[3], key=lambda x: int(x[0].split('_')[1]))]

    # Proportional stacked bar graph values
    if value_type == 'proportion':
        plt.ylabel('Proportion of Labeling')
        col_totals = np.sum(div_lists, axis=0)
        div_lists = np.nan_to_num(np.array(div_lists) / col_totals) * 100

    else:
        plt.ylabel('Absolute Value of Pixels')

    bars = []
    bottoms = np.zeros(4)
    for idx, division in enumerate(div_lists):
        bars.append(plt.bar(
            ind, division, bottom=bottoms, color=colors[idx], width=width))
        bottoms += division

    plt.title(title)
    plt.xticks(ind, ('ARA 86', 'ARA 90', 'ARA 96', 'ARA 100'))
    plt.legend((bars[0][0], bars[1][0], bars[2][0], bars[3][0]),
               ('SC.m', 'SC.cm', 'SC.cl', 'SC.l'))

    plt.savefig(out_path, dpi=600)
    plt.close()


def plot_stacked(div_lists, colors, bar_num, out_path):
    lvls = bar_num  # number of bars
    ind = np.arange(lvls)  # the locations for the groups
    width = 0.35  # the width of the bars

    bars = []
    bottoms = np.zeros(bar_num)
    for idx, division in enumerate(div_lists):
        bars.append(plt.bar(
            ind, division, bottom=bottoms, color=colors[idx], width=width))
        bottoms += division

    plt.savefig(out_path, dpi=600)
    plt.close()


if __name__ == '__main__':
    main()
