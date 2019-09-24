#!/usr/bin/env python
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from cic_dis import cic_utils
import argparse
import cPickle as pickle
import os
import json
matplotlib.use('Agg')


parser = argparse.ArgumentParser(
    description="Converts aggregated overlap output to connectivity "
                "matrix csv")

parser.add_argument('-t', '--tracer_type',
                    help='"ret" for retrograde or "ant" for anterograde',
                    required=True)

parser.add_argument('-fs', '--fontsize',
                    help='Font size of tick labels in x and y',
                    type=int,
                    default=5)

parser.add_argument('-i', '--input_matrix_csv_path',
                    help='Input aggregated overlap path',
                    required=True)

parser.add_argument('-rgb', '--rgb_color',
                    help="RGB string ex. 'r,g,b' ",
                    default='0,0,0')

parser.add_argument('-br', '--by_region',
                    help="Sorts sections by region, using hierarchy json file",
                    action='store_true')

parser.add_argument('-s', '--save',
                    help='Save generated figure',
                    action='store_true')


# READ ARGS
args = vars(parser.parse_args())

tracer_type = args['tracer_type']
fontsize = args['fontsize']
input_matrix_csv_path = args['input_matrix_csv_path']
save_figure = args['save']
rgb = tuple(args['rgb_color'].split(','))
by_region = args['by_region']


# Sort by region? find a better way to do this also need json file with
# allen institute hierarchy
def sort_by_region(region_lst, values_lst):
    hierarchy_file = "../../hierarchy.json"
    assert os.path.isfile(hierarchy_file), "Hierarchy file {} missing".format(
        hierarchy_file)

    with open(hierarchy_file, 'r') as f:
        json_string = f.read()
        structure_dict = json.loads(json_string)

    by_region_dict = {}
    hits = 0

    # iterates through the regions
    for indx, region in enumerate(region_lst):

        # regions from ai don't have the underscore
        region = region.replace("_", "").replace("-", "").lower()
        found = False

        # iterates through the structure lst
        for structure in structure_dict:
            if structure not in by_region_dict:
                by_region_dict[structure] = [[], []]

            # iterates through regions of substructures
            for substructure in structure_dict[structure]:

                if region == substructure.replace("-", "").lower():
                    hits += 1
                    found = True

                    by_region_dict[structure][0].append(region_lst[indx])
                    by_region_dict[structure][1].append(values_lst[indx])
                    break

        if not found:
            # check if they are custom
            if region == 'entl6':
                by_region_dict["Hippocampal formation"][0].append(
                    region_lst[indx])
                by_region_dict["Hippocampal formation"][1].append(
                    values_lst[indx])
                hits += 1
            elif region in ['bstbac']:
                by_region_dict["Pallidum"][0].append(region_lst[indx])
                by_region_dict["Pallidum"][1].append(values_lst[indx])
                hits += 1
            elif region in ['mdi', 'vl']:
                by_region_dict["Thalamus"][0].append(region_lst[indx])
                by_region_dict["Thalamus"][1].append(values_lst[indx])
                hits += 1
            elif region in ['hy', 'pvrpd']:
                by_region_dict["Hypothalamus"][0].append(region_lst[indx])
                by_region_dict["Hypothalamus"][1].append(values_lst[indx])
                hits += 1
            elif region in ['culmo']:
                by_region_dict["Cerebellum"] = [[], []]
                by_region_dict["Cerebellum"][0].append(region_lst[indx])
                by_region_dict["Cerebellum"][1].append(values_lst[indx])
                hits += 1
            else:
                print(region, " was not found and actual ", region_lst[indx])

    # After completing, join the lsts
    master_region_lst = []
    master_values_lst = []

    for struct in by_region_dict:
        # print(struct, " has ", len(by_region_dict[struct][0]))
        # [0] lst regions
        master_region_lst += by_region_dict[struct][0]
        # [1] lst values
        master_values_lst += by_region_dict[struct][1]

    print("Hits: ", hits)

    assert hits == len(region_lst), "Not all regions were found, :["
    return master_region_lst, master_values_lst


''' Example
# BLAam
matrix_csv_ret_path = './norm_ctx_mat_agg_BLAam_bar_chart_ret_roi.csv'
matrix_csv_ant_path = './norm_ctx_mat_agg_BLAam_bar_chart_ant_roi.csv'
rgb = (82, 63, 195)
# '''


# convert rgb colors to 0 to 1 scale
bar_color = map(lambda val: int(val) / 255.0, rgb)

fig, ax = plt.subplots()

ants = []
rets = []
rois = []

#  Retrograde
if tracer_type == 'ret':
    assert os.path.isfile(input_matrix_csv_path), \
        "Ret file doesn't exist {}".format(input_matrix_csv_path)
    assert "ret" in input_matrix_csv_path, \
        "Are you sure this is a retrograde file?"
    (row_roi_name_ret_npa, col_roi_name_ret_npa, ctx_mat_ret_npa) = \
        cic_utils.read_ctx_mat(input_matrix_csv_path)
    print("RETROGRADE")
    print("USING: {}".format(input_matrix_csv_path))

    for idx in range(len(ctx_mat_ret_npa)):
        rets.append(ctx_mat_ret_npa[idx][0])
        rois.append(row_roi_name_ret_npa[idx])

    print("ret len: ", len(ctx_mat_ret_npa))

    assert len(rets) == len(rois), "Knot the same length!!!!"

    # Seperate rois by region in hierarchy_file
    if by_region:
        rois, rets = sort_by_region(rois, rets)

    x = np.arange(len(rets))

    ax.bar(x, rets, align='center', color=bar_color, zorder=10)
    ax.set(title='Retrograde')


#  Anterograde
elif tracer_type == 'ant':
    assert os.path.isfile(input_matrix_csv_path), "Ant file doesn't exist"
    assert "ant" in input_matrix_csv_path, \
        "Are you sure this is an Anterograde file?"
    print("ANTEROGRADE")
    print("USING: {}".format(input_matrix_csv_path))

    (row_roi_name_ant_npa, col_roi_name_ant_npa, ctx_mat_ant_npa) = \
        cic_utils.read_ctx_mat(input_matrix_csv_path)

    for idx in range(len(ctx_mat_ant_npa[0])):
        ants.append(ctx_mat_ant_npa[0][idx])
        rois.append(col_roi_name_ant_npa[idx])

    print("Total number in ants: ", len(ants))
    assert len(ctx_mat_ant_npa[0]) == len(ants), "ants length don't match"

    assert len(ants) == len(rois), "Knot the same length!!!!"

    # Seperate rois by region in hierarchy_file
    if by_region:
        rois, ants = sort_by_region(rois, ants)

    x = np.arange(len(ants))
    ax.bar(x, ants, align='center', color=bar_color, zorder=10)
    ax.set(title='Anterograde')

else:
    raise ValueError("Region type doesn't match anything")

ax.set_xticks(x)
ax.set_xticklabels(rois)

ax.invert_xaxis()
plt.setp(ax.get_xticklabels(), rotation=70, ha="center", fontsize=fontsize)

# Save figure
if save_figure:
    out_path = input_matrix_csv_path.replace('.csv',
                                             '_bar_graph.png')
    plt.savefig(out_path, dpi=600)
    pickle_path = cic_utils.pickle_path(out_path)
    pickle.dump(args, open(pickle_path, "wb"))


# Showing the plot
else:
    plt.show()
