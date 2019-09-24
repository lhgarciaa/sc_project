#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import cPickle as pickle
from cic_dis import cic_utils
import csv
import numpy as np

'''
-ant_i and -ret_i required, output to ant_i directory
Need to hide original -ant_i, perhaps should create a new directory
'''


def main():
    parser = argparse.ArgumentParser(
        description="Joins anterograde matrix and retrograde matrix")
    parser.add_argument('-ant_i', '--ant_input_ctx_mat_csv',
                        help='Anterograde connectivity matrix csv',
                        required=True)
    parser.add_argument('-ret_i', '--ret_input_ctx_mat_csv',
                        help='Retrograde connectivity matrix csv',
                        required=True)
    parser.add_argument('-o', '--output_cmb_ctx_mat_csv',
                        help='Output combined connectivity matrix csv',
                        required=True)
    parser.add_argument('-n', '--normalize_values',
                        help='Normalize retrograde and anterograde values',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Print extra information about normalization',
                        action='store_true')

    args = vars(parser.parse_args())

    ant_input_csv_path = args['ant_input_ctx_mat_csv']
    ret_input_csv_path = args['ret_input_ctx_mat_csv']
    output_ctx_mat_csv = args['output_cmb_ctx_mat_csv']
    normalize = args['normalize_values']
    verbose = args['verbose']

    assert os.path.isfile(ant_input_csv_path),\
        "can't find anterograde csv file {}".format(ant_input_csv_path)

    assert os.path.isfile(ret_input_csv_path),\
        "can't find retrograde csv file {}".format(ret_input_csv_path)

    # OPEN, READ INPUT CSV ANTEROGRADE
    if verbose:
        print("reading {}".format(ant_input_csv_path))
    (ant_row_roi_name_npa, ant_col_roi_name_npa, ant_ctx_mat_npa) = \
        cic_utils.read_ctx_mat(ant_input_csv_path)
    ant_norm_ctx_mat = []

    # Go through ant_row_roi_name_npa
    for idx in xrange(ant_row_roi_name_npa.size):
        # If normalize true
        if normalize:
            row_max, row_min = row_max_min(ant_ctx_mat_npa, idx)
            a_row = map(lambda x: normalize_calc(row_max, row_min, x),
                        ant_ctx_mat_npa[idx])
        else:
            a_row = map(lambda x: x, ant_ctx_mat_npa[idx])

        ant_norm_ctx_mat.append(a_row)

    # OPEN, READ INPUT CSV RETROGRADE
    if verbose:
        print("reading {}".format(ant_input_csv_path))
    (ret_row_roi_name_npa, ret_col_roi_name_npa, ret_ctx_mat_npa) = \
        cic_utils.read_ctx_mat(ret_input_csv_path)

    # Go through ret_col_roi_name_npa
    for idx in xrange(ret_col_roi_name_npa.size):
        if normalize:
            col_max, col_min = col_max_min(ret_ctx_mat_npa, idx)
            a_col = map(lambda x: normalize_calc(col_max, col_min, x),
                        ret_ctx_mat_npa[:, idx])
        else:
            a_col = map(lambda x: x, ret_ctx_mat_npa[:, idx])
        ret_ctx_mat_npa[:, idx] = a_col

    # Write rows to CSV output file
    with open(output_ctx_mat_csv, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)

        header_row = [''] + \
            ant_col_roi_name_npa.tolist() + \
            ret_col_roi_name_npa.tolist()
        csvwriter.writerow(header_row)

        for idx in xrange(ant_row_roi_name_npa.size):
            ant_row = [ant_row_roi_name_npa[idx]] + \
                      ant_norm_ctx_mat[idx] + \
                      ([''] * ret_col_roi_name_npa.size)

            csvwriter.writerow(ant_row)

        for idx in xrange(ret_row_roi_name_npa.size):
            ret_row = [ret_row_roi_name_npa[idx]] + \
                      ([''] * ant_col_roi_name_npa.size) + \
                      list(ret_ctx_mat_npa[idx])

            csvwriter.writerow(ret_row)

    print("Wrote combined connection matrix csv to {}".format(
        output_ctx_mat_csv))

    output_pickle_path = cic_utils.pickle_path(output_ctx_mat_csv)
    pickle_dct = cic_utils.pickle_dct(args)
    pickle.dump(pickle_dct, open(output_pickle_path, "wb"))


def normalize_calc(maximum, minimum, value):
    if maximum - minimum == 0:
        return minimum
    return float(value - minimum)/float(maximum - minimum)


def row_max_min(ctx_mat_npa, idx):
    return np.amax(ctx_mat_npa[idx]), np.amin(ctx_mat_npa[idx])


def col_max_min(ctx_mat_npa, idx):
    return np.amax(ctx_mat_npa[:, idx]), np.amin(ctx_mat_npa[:, idx])


if __name__ == "__main__":
    main()
