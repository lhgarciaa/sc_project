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
    tracer_mode = 'anterograde'
    verbose = args['verbose']

    # check input path is actually valid
    assert os.path.isfile(input_csv_path),\
        "can't find input csv file {}".format(input_csv_path)

    # OPEN, READ INPUT CSV
    if verbose:
        print("reading {}".format(input_csv_path))
    (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) = \
        cic_utils.read_ctx_mat(input_csv_path)

    # use a simple method to determine if anterograde or retrograde
    #  more importantly, operate on rows or columns accordingly
    if 'ret' in input_csv_path:
        tracer_mode = 'retrograde'

    if tracer_mode == 'anterograde':
        # get max row
        max_row_idx = -1
        max_total = -1
        for idx in xrange(len(row_roi_name_npa)):
            if(cic_utils.row_total(ctx_mat_npa=ctx_mat_npa, idx=idx) >
               max_total):
                max_row_idx = idx
                max_total = cic_utils.row_total(ctx_mat_npa=ctx_mat_npa,
                                                idx=idx)
        if verbose:
            print("Found row {} as max total sum with {}".format(
                row_roi_name_npa[max_row_idx], max_total))

    if tracer_mode == 'retrograde':
        # get max col
        max_col_idx = -1
        max_total = -1
        for idx in xrange(len(col_roi_name_npa)):
            if(cic_utils.col_total(ctx_mat_npa=ctx_mat_npa, idx=idx) >
               max_total):
                max_col_idx = idx
                max_total = cic_utils.col_total(ctx_mat_npa=ctx_mat_npa,
                                                idx=idx)
        if verbose:
            print("Found col {} as max total sum with {}".format(
                col_roi_name_npa[max_col_idx], max_total))

    with open(output_ctx_mat_csv, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)

        if tracer_mode == 'anterograde':
            header_row = [''] + list(col_roi_name_npa)
            csvwriter.writerow(header_row)
            for idx in xrange(len(row_roi_name_npa)):
                # now normalize to max and write
                if idx != max_row_idx:
                    row_total = cic_utils.row_total(ctx_mat_npa=ctx_mat_npa,
                                                    idx=idx)
                    fact = float(max_total)/float(row_total)
                    if verbose:
                        print(
                            "Normalizing {} row total {} with factor {}".
                            format(row_roi_name_npa[idx], row_total, fact))
                    norm_row = cic_utils.row_elem_mult(
                        ctx_mat_npa=ctx_mat_npa,
                        idx=idx,
                        fact=fact,
                        max_prod=1.0)

                    csvwriter.writerow([row_roi_name_npa[idx]] +
                                       list(norm_row))
                else:
                    csvwriter.writerow([row_roi_name_npa[idx]] +
                                       list(ctx_mat_npa[idx]))

        elif tracer_mode == 'retrograde':
            header_row = [''] + list(col_roi_name_npa)
            csvwriter.writerow(header_row)
            norm_cols = []
            for idx in xrange(len(col_roi_name_npa)):
                # now normalize to max and write
                if idx != max_col_idx:
                    col_total = cic_utils.col_total(ctx_mat_npa=ctx_mat_npa,
                                                    idx=idx)
                    fact = float(max_total)/float(col_total)
                    if verbose:
                        print(
                            "Normalizing {} col total {} with factor {}".
                            format(col_roi_name_npa[idx], col_total, fact))
                    norm_col = cic_utils.col_elem_mult(
                        ctx_mat_npa=ctx_mat_npa,
                        idx=idx,
                        fact=fact,
                        max_prod=None)  # pass None to prevent max clipping
                else:
                    norm_col = ctx_mat_npa[:, idx]

                norm_cols.append(norm_col)

            # zip the columns into rows of len(col_roi_name_npa) length
            norm_rows = zip(*norm_cols)

            for idx, norm_row in enumerate(norm_rows):
                csvwriter.writerow([row_roi_name_npa[idx]] + list(norm_row))

        else:
            assert 0, "invalid mode {}".format(tracer_mode)

    if verbose:
        print("wrote to {}".format(output_ctx_mat_csv))

    output_pickle_path = cic_utils.pickle_path(output_ctx_mat_csv)
    pickle_dct = cic_utils.pickle_dct(args)
    pickle.dump(pickle_dct, open(output_pickle_path, "wb"))


if __name__ == "__main__":
    main()
