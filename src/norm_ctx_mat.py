#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import cPickle as pickle
from cic_dis import cic_utils
import csv


def main():
    parser = argparse.ArgumentParser(
        description="Normalizes connectivity matrix")
    parser.add_argument('-i', '--input_ctx_mat_csv',
                        help='Input connectivity matrix csv',
                        required=True)
    parser.add_argument('-o', '--output_ctx_mat_csv',
                        help='Output path for normalized ctx mat csv',
                        required=True)
    parser.add_argument('-v', '--verbose',
                        help='Print extra information about normalization',
                        action='store_true')

    args = vars(parser.parse_args())

    input_csv_path = args['input_ctx_mat_csv']
    output_ctx_mat_csv = args['output_ctx_mat_csv']
    verbose = args['verbose']

    # check input path is actually valid
    assert os.path.isfile(input_csv_path),\
        "can't find input csv file {}".format(input_csv_path)

    # OPEN, READ INPUT CSV
    if verbose:
        print("reading {}".format(input_csv_path))
    (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) = \
        cic_utils.read_ctx_mat(input_csv_path)

    # get max row
    max_row_idx = -1
    max_total = -1
    for idx in xrange(len(row_roi_name_npa)):
        if cic_utils.row_total(ctx_mat_npa=ctx_mat_npa, idx=idx) > max_total:
            max_row_idx = idx
            max_total = cic_utils.row_total(ctx_mat_npa=ctx_mat_npa, idx=idx)

    if verbose:
        print("Found max total of {} at row index {}".format(
            max_total, max_row_idx))
        print("writing to {}".format(output_ctx_mat_csv))
    with open(output_ctx_mat_csv, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        header_row = [''] + list(col_roi_name_npa)
        csvwriter.writerow(header_row)
        for idx in xrange(len(row_roi_name_npa)):
            # now normalize to max and write
            if idx != max_row_idx:
                row_total = cic_utils.row_total(ctx_mat_npa=ctx_mat_npa,
                                                idx=idx)
                fact = float(max_total)/float(row_total)
                if verbose:
                    print("Normalizing row index {} with factor {}".format(
                        idx, fact))
                norm_row = cic_utils.elem_mult(
                    ctx_mat_npa=ctx_mat_npa,
                    idx=idx,
                    fact=fact,
                    max_prod=1.0)

                csvwriter.writerow([row_roi_name_npa[idx]] + list(norm_row))
            else:
                csvwriter.writerow([row_roi_name_npa[idx]] +
                                   list(ctx_mat_npa[idx]))

    output_pickle_path = cic_utils.pickle_path(output_ctx_mat_csv)
    pickle_dct = cic_utils.pickle_dct(args)
    pickle.dump(pickle_dct, open(output_pickle_path, "wb"))


if __name__ == "__main__":
    main()
