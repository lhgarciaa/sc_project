import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from cic_dis import cic_utils
import argparse
import os
import pdb
import json

parser = argparse.ArgumentParser(
    description="Converts aggregated overlap output to connectivity "
                "matrix csv")

parser.add_argument('-r', '--region',
                    help='type of region',
                    required=True)

parser.add_argument('-fs', '--fontsize',
                    help='Font size of tick labels in x and y',
                    type=int,
                    default=5)

# READ ARGS
args = vars(parser.parse_args())

region_type = args['region']
fontsize = args['fontsize']

hierarchy_file = "../../hierarchy.json"
assert os.path.isfile(hierarchy_file), "Hierarchy file is not were it's supposed to be"

with open(hierarchy_file, 'r') as f:
    json_string = f.read()
    structure_dict = json.loads(json_string)


# Sort by region? There should be a better way to do this
def sort_by_region(region_lst, values_lst):
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
                by_region_dict["Hippocampal formation"][0].append(region_lst[indx])
                by_region_dict["Hippocampal formation"][1].append(values_lst[indx])
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


'''
# BLAam
matrix_csv_ret_path = '../../houri/BLA/publish_BLAam_bar_chart_ret/norm_ctx_mat_agg_BLAam_bar_chart_ret_roi/norm_ctx_mat_agg_BLAam_bar_chart_ret_roi.csv'      # NOQA
matrix_csv_ant_path = '../../pl_probelauf/publish_BLAam_bar_chart_ant/norm_ctx_mat_agg_BLAam_bar_chart_ant_roi/norm_ctx_mat_agg_BLAam_bar_chart_ant_roi.csv'
rgb = (82, 63, 195)
# '''
'''
# BLAal
matrix_csv_ret_path = "../../houri/BLA/publish_BLAal_bar_chart_ret/not_norm_ctx_mat_agg_BLAal_bar_chart_ret_roi/not_norm_ctx_mat_agg_BLAal_bar_chart_ret_roi.csv"  # NOQA
matrix_csv_ant_path = "../../houri/BLA/publish_BLAal_bar_chart_ant/not_norm_ctx_mat_agg_BLAal_bar_chart_ant_roi/not_norm_ctx_mat_agg_BLAal_bar_chart_ant_roi.csv"
rgb = (187, 63, 195)
# '''
'''
# BLAp
matrix_csv_ret_path = "../../houri/BLA/publish_BLAp_bar_chart_ret/not_norm_ctx_mat_agg_BLAp_bar_chart_ret_roi/not_norm_ctx_mat_agg_BLAp_bar_chart_ret_roi.csv"  # NOQA
matrix_csv_ant_path = "../../houri/BLA/publish_BLAp_bar_chart_ant/not_norm_ctx_mat_agg_BLAp_bar_chart_ant_roi/not_norm_ctx_mat_agg_BLAp_bar_chart_ant_roi.csv"
rgb = (63, 128, 193)
# '''
'''
# BLAv
matrix_csv_ret_path = "../../houri/BLA/publish_BLAv_bar_chart_ret/not_norm_ctx_mat_agg_BLAv_bar_chart_ret_roi/not_norm_ctx_mat_agg_BLAv_bar_chart_ret_roi.csv"  # NOQA
matrix_csv_ant_path = "../../houri/BLA/publish_BLAv_bar_chart_ant/not_norm_ctx_mat_agg_BLAv_bar_chart_ant_roi/not_norm_ctx_mat_agg_BLAv_bar_chart_ant_roi.csv"
rgb = (43, 31, 115)
# '''
'''
# BMAp
matrix_csv_ret_path = "../../houri/BLA/publish_BMAp_bar_chart_ret/not_norm_ctx_mat_agg_BMAp_bar_chart_ret_roi/not_norm_ctx_mat_agg_BMAp_bar_chart_ret_roi.csv"  # NOQA
matrix_csv_ant_path = "../../houri/BLA/publish_BMAp_bar_chart_ant/not_norm_ctx_mat_agg_BMAp_bar_chart_ant_roi/not_norm_ctx_mat_agg_BMAp_bar_chart_ant_roi.csv"
rgb = (108, 31, 115)
# '''
# '''
# LA
matrix_csv_ret_path = "../../houri/BLA/publish_LA_bar_chart_ret/not_norm_ctx_mat_agg_LA_bar_chart_ret_roi/not_norm_ctx_mat_agg_LA_bar_chart_ret_roi.csv"  # NOQA
matrix_csv_ant_path = "../../houri/BLA/publish_LA_bar_chart_ant/not_norm_ctx_mat_agg_LA_bar_chart_ant_roi/not_norm_ctx_mat_agg_LA_bar_chart_ant_roi.csv"
rgb = (31, 82, 115)
# '''
'''
# BLAac
matrix_csv_ret_path = "../../houri/BLA/publish_BLAac_bar_chart_ret/not_norm_ctx_mat_agg_BLAac_bar_chart_ret_roi/not_norm_ctx_mat_agg_BLAac_bar_chart_ret_roi.csv"  # NOQA
matrix_csv_ant_path = "../../houri/BLA/publish_BLAac_bar_chart_ant/not_norm_ctx_mat_agg_BLAac_bar_chart_ant_roi/not_norm_ctx_mat_agg_BLAac_bar_chart_ant_roi.csv"
rgb = (3, 144, 102)
# '''

# print("this is rgb: ", rgb)
bar_color = map(lambda val: val / 255.0, rgb)

fig, ax = plt.subplots()

ants = []
rets = []
rois = []

#  Retrograde
if region_type == 'ret':
    assert os.path.isfile(matrix_csv_ret_path), "Ret file doesn't exist"
    assert "ret" in matrix_csv_ret_path, "Are you sure this is a retrograde file?"
    (row_roi_name_ret_npa, col_roi_name_ret_npa, ctx_mat_ret_npa) = cic_utils.read_ctx_mat(matrix_csv_ret_path)
    print("RETROGRADE")
    print("USING: {}".format(matrix_csv_ret_path))

    for idx in range(len(ctx_mat_ret_npa)):
        rets.append(ctx_mat_ret_npa[idx][0])
        rois.append(row_roi_name_ret_npa[idx])

    print("ret len: ", len(ctx_mat_ret_npa))

    assert len(rets) == len(rois), "Knot the same length!!!!"

    rois, rets = sort_by_region(rois, rets)
    x = np.arange(len(rets))

    ax.bar(x, rets, align='center', color=bar_color, zorder=10)
    ax.set(title='Retrograde')


#  Anterograde
elif region_type == 'ant':
    assert os.path.isfile(matrix_csv_ant_path), "Ant file doesn't exist"
    assert "ant" in matrix_csv_ant_path, "Are you sure this is an Anterograde file?"
    print("ANTEROGRADE")
    print("USING: {}".format(matrix_csv_ant_path))

    (row_roi_name_ant_npa, col_roi_name_ant_npa, ctx_mat_ant_npa) = cic_utils.read_ctx_mat(matrix_csv_ant_path)

    for idx in range(len(ctx_mat_ant_npa[0])):
        ants.append(ctx_mat_ant_npa[0][idx])
        rois.append(col_roi_name_ant_npa[idx])

    print("Total number in ants: ", len(ants))
    assert len(ctx_mat_ant_npa[0]) == len(ants), "ants length don't match"

    assert len(ants) == len(rois), "Knot the same length!!!!"
    # pdb.set_trace()
    rois, ants = sort_by_region(rois, ants)
    # pdb.set_trace()

    x = np.arange(len(ants))
    ax.bar(x, ants, align='center', color=bar_color, zorder=10)
    ax.set(title='Anterograde')

else:
    raise ValueError("Region type doesn't match anything")

ax.set_xticks(x)
ax.set_xticklabels(rois)

ax.invert_xaxis()
plt.setp(ax.get_xticklabels(), rotation=70, ha="center", fontsize=fontsize)

# Showing the plot
plt.show()
