# CIC utilities typically related to i/o
import os
import sys
import csv
import numpy as np


def pickle_path(input_path):
    basename = os.path.basename(input_path)
    ext = os.path.splitext(input_path)[1]
    new_basename = '.' + basename.replace(ext, '.p')
    return input_path.replace(basename, new_basename)


def pickle_dct(parser_args):
    pickle_dct = parser_args
    pickle_dct['script'] = sys.argv[0]
    pickle_dct['cwd'] = os.getcwd()

    return pickle_dct


# converts x and '' to 1.0 and 0.0
# NOTE: returns floats
# returns tuple (
#  row_roi_name_npa = np.array(roi_name_arr),
#  col_roi_name_npa = np.array(roi_name_arr),
#  ctx_mat_npa = np.array(connectivity_matrix_arr_arr)
def read_ctx_mat(input_csv_path):
    col_roi_name_arr = []
    row_roi_name_arr = []
    ctx_mat_arr_arr = []

    with open(input_csv_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile)

        # extract csv into numpy array
        for row_index, row in enumerate(csvreader):

            # read ROI names
            if row_index == 0:
                label_row = row[1:len(row)]
                col_roi_name_arr = [x.strip() for x in label_row]
            else:
                row_roi_name_arr.append(row[0].strip())

                # convert 'x' to 1
                x_to_1_arr = [int(x == 'x') or x for x in row[1:len(row)]]

                # convert blank to '0'
                blank_to_zero_char = [x or '0' for x in x_to_1_arr]
                # check that nonzero values are within roi name arr
                assert len(blank_to_zero_char) <= len(col_roi_name_arr)\
                    or max(np.where(np.array(blank_to_zero_char) != '0')[0]) <\
                    len(col_roi_name_arr),\
                    "number of connectivity value row length {} does not "
                "match ROI label length {}".\
                    format(blank_to_zero_char, col_roi_name_arr)

                # convert all cells to floats
                ctx_mat_arr_arr.append(
                    [float(x) for x in blank_to_zero_char])

    return (np.array(row_roi_name_arr),
            np.array(col_roi_name_arr),
            np.array(ctx_mat_arr_arr))


# note if the same rois are in a different order, is_sq returns false
def is_sq(row_roi_name_npa, col_roi_name_npa, ctx_mat_npa):
    shape = ctx_mat_npa.shape
    # also test that rois are the same (duh)
    return (row_roi_name_npa.tolist() == col_roi_name_npa.tolist() and
            len(col_roi_name_npa) == len(row_roi_name_npa) and
            (shape[0] == shape[1]) and
            (len(col_roi_name_npa) == shape[0]))


# returns tuple (
#  pad_row_roi_name_npa = np.array(roi_name_arr),
#  pad_col_roi_name_npa = np.array(roi_name_arr),
#  pad_ctx_mat_npa = np.array(connectivity_matrix_arr_arr)
#                              )
def pad_rect_ctx_mat_to_sq(row_roi_name_npa, col_roi_name_npa, ctx_mat_npa):
    if is_sq(col_roi_name_npa=col_roi_name_npa,
             row_roi_name_npa=row_roi_name_npa,
             ctx_mat_npa=ctx_mat_npa):
        return(row_roi_name_npa, ctx_mat_npa)
    else:
        shape = ctx_mat_npa.shape
        max_dim = max(shape[0], shape[1])
        assert len(row_roi_name_npa) == max_dim or \
            len(col_roi_name_npa) == max_dim

        # pad matrix
        pad_ctx_mat_npa = np.zeros(
            max_dim * max_dim
        ).reshape(
            (max_dim, max_dim))
        pad_ctx_mat_npa[:shape[0], :shape[1]] = ctx_mat_npa

        # pad roi npas
        zeros_pad_roi_name_npa = np.zeros(max_dim)
        none_pad_roi_name_npa = np.array(
            ['NONE_{0:05}'.format(x_index) for
             x_index, x in enumerate(zeros_pad_roi_name_npa)])

        pad_row_roi_name_npa = row_roi_name_npa
        pad_col_roi_name_npa = col_roi_name_npa

        if len(row_roi_name_npa) < max_dim:
            none_pad_roi_name_npa[:len(row_roi_name_npa)] = row_roi_name_npa
            pad_row_roi_name_npa = none_pad_roi_name_npa

        elif len(col_roi_name_npa) < max_dim:
            none_pad_roi_name_npa[:len(col_roi_name_npa)] = col_roi_name_npa
            pad_col_roi_name_npa = none_pad_roi_name_npa
        return (pad_row_roi_name_npa, pad_col_roi_name_npa, pad_ctx_mat_npa)


# returns tuple(
# sq_roi_name_npa = np.array(roi_name_arr)
# sq_ctx_mat_npa = np.array(ctx_mat_arr_arr)
#                                                      )
def conv_rect_ctx_mat_to_sq(row_roi_name_npa, col_roi_name_npa, ctx_mat_npa):
    if is_sq(col_roi_name_npa=col_roi_name_npa,
             row_roi_name_npa=row_roi_name_npa,
             ctx_mat_npa=ctx_mat_npa):
        return(row_roi_name_npa, ctx_mat_npa)
    else:
        # create set of all rois
        sq_roi_name_lst = \
            sorted(set(np.append(col_roi_name_npa, row_roi_name_npa)))
        row_roi_name_lst = row_roi_name_npa.tolist()
        col_roi_name_lst = col_roi_name_npa.tolist()

        # create new matrix arr that is N x N in size where N=len(set all rois)
        # march through original matrix
        sq_ctx_mat_arr_arr = []
        for row_index, row_roi in enumerate(sq_roi_name_lst):
            row_arr = []
            for col_index, col_roi in enumerate(sq_roi_name_lst):
                # if row_roi and col_roi connected, mark as connected
                if row_roi in row_roi_name_npa and col_roi in col_roi_name_npa:
                    row_index = row_roi_name_lst.index(row_roi)
                    col_index = col_roi_name_lst.index(col_roi)
                    row_arr.append(ctx_mat_npa[row_index][col_index])
                else:
                    row_arr.append(0)

            sq_ctx_mat_arr_arr.append(row_arr)

        return (np.array(sq_roi_name_lst), np.array(sq_ctx_mat_arr_arr))


# CHECK FORMATTING OF MATRICES AND ARRAYS
#  dup_check_roi_lst : list of all rois found so far
#  roi : ROI string with strip() but no lowercase applied
def dup_check_container(dup_check_roi_container, input_csv_path):
    lower_lst = [x.lower() for x in dup_check_roi_container]
    dup_lst = [x for x in lower_lst if lower_lst.count(x) > 1]
    assert len(dup_lst) == 0,\
        "Uh oh, it appears {} is/are in {} multiple times".\
        format(set(dup_lst), input_csv_path)


# build community structure dict
# input
#  ci : community index list as defined in louvain
#  roi_name_npa : numpy array of roi names
#  returns
#  community_structure_dict = { com_1 : [roi_name1, ... ], com_2 : [...] }
def build_community_structure_dict(ci, roi_name_npa):
    community_structure_dict = {}
    for roi_index, roi in enumerate(roi_name_npa):
        community_list = community_structure_dict.get(ci[roi_index], [])
        community_list.append(roi)
        community_structure_dict[ci[roi_index]] = community_list
    return community_structure_dict


# returns
#  {'run' : number of run
#   'q' : q value
#   'num_communities' : number of communities found at run
#   'gamma' : gamma value used as input for run
#  n'community_structure' : community_structure_dict as defined in above method
def build_louvain_run_dict(run_index, q, community_structure_dict, gamma):
        return {
            'run': run_index + 1,
            'q': q,
            'num_communities': len(community_structure_dict.keys()),
            'gamma': gamma,
            'community_structure': community_structure_dict}
