#!/usr/bin/env python
from __future__ import print_function
import argparse
from cic_dis import cic_overlap
import glob
import csv
from cic_dis import cic_utils
import cPickle as pickle


def main():
    parser = argparse.ArgumentParser(
        description="Aggregates a wildcard of overlap csv files into output "
        "csv file.")
    parser.add_argument('-i', '--input_overlap_csv_wildcard',
                        help='Input wildcard for overlap csv',
                        required=True)
    parser.add_argument('-o', '--output_agg_overlap_csv',
                        help='Output aggreated overlap csv',
                        required=True)

    parser.add_argument('-r', '--replacement_injection_site',
                        help='Replacement injection site',
                        required=False)

    parser.add_argument('-v', '--verbose',
                        help='Print extra information about aggregation',
                        action='store_true')

    # READ ARGS
    args = vars(parser.parse_args())

    input_overlap_csv_wildcard = args['input_overlap_csv_wildcard']
    # sort glob for consistency of test results
    overlap_csv_path_lst = sorted(glob.glob(input_overlap_csv_wildcard))
    output_agg_overlap_csv = args['output_agg_overlap_csv']
    # get replacement injection site if it's there
    ris = args['replacement_injection_site']
    replace_inj_site = ris is not None

    assert len(overlap_csv_path_lst) > 0,\
        "no input csv files matching {}".format(input_overlap_csv_wildcard)

    # OPEN, READ INPUT CSV
    all_rows = []
    for overlap_csv_path in overlap_csv_path_lst:
        (overlap_csv_meta_dct, overlap_header_lst, overlap_csv_dct_rows) = \
            cic_overlap.read_overlap_csv_dct_rows(overlap_csv_path)

        #  first check for meta keys that could be missing
        if 'Connection Lens Version' not in overlap_csv_meta_dct.keys() + \
           overlap_header_lst:
            overlap_csv_meta_dct['Connection Lens Version'] = 'None'
        if 'Seconday Injection Site' not in overlap_csv_meta_dct.keys() + \
           overlap_header_lst:
            overlap_csv_meta_dct['Seconday Injection Site'] = 'None'
        # replace injection site with replacement value specified on cl
        if replace_inj_site:
            overlap_csv_meta_dct['Injection Site'] = ris

        # if writing first row, then write header
        if len(all_rows) == 0:
            meta_dct_keys = sorted(overlap_csv_meta_dct.keys())
            overlap_dct_keys = sorted(overlap_header_lst)
            new_header = meta_dct_keys + overlap_dct_keys
            all_rows.append(new_header)
        front_cols = []
        for key in meta_dct_keys:
            front_cols.append(overlap_csv_meta_dct[key])
        # for each overlap_csv_dct row
        #  place vals in same order on each row w/ blank if no value
        for row in overlap_csv_dct_rows:
            overlap_val_row = []
            for key in overlap_dct_keys:
                overlap_val_row.append(row.get(key, ''))
            all_rows.append(front_cols + overlap_val_row)

    with open(output_agg_overlap_csv, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(all_rows)

    output_pickle_path = cic_utils.pickle_path(output_agg_overlap_csv)
    pickle_dct = cic_utils.pickle_dct(args)
    pickle.dump(pickle_dct, open(output_pickle_path, "wb"))


if __name__ == '__main__':
    main()
