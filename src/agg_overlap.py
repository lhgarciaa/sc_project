#!/usr/bin/env python
from __future__ import print_function
import argparse
from cic_dis import cic_overlap
import glob
import csv
import os
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
    parser.add_argument('-r_csv', '--replace_csv',
                        help='csv with replacement SC injection site names',
                        required=False)
    parser.add_argument('-div', '--only_division_regions',
                        help='Only copies SC division region rows',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Print extra information about aggregation',
                        action='store_true')

    # READ ARGS
    args = vars(parser.parse_args())

    input_overlap_csv_wildcard = args['input_overlap_csv_wildcard']
    # sort glob for consistency of test results
    overlap_csv_path_lst = sorted(glob.glob(input_overlap_csv_wildcard))
    output_agg_overlap_csv = args['output_agg_overlap_csv']
    division_regions = args['only_division_regions']
    # get replacement injection site if it's there
    ris = args['replacement_injection_site']
    replace_inj_site = ris is not None

    replace_csv = args['replace_csv']
    if replace_csv:
        rep_dict = replacement_csv_to_dict(replace_csv)
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
            # overlap_csv_meta_dct['Injection Site'] = ris
            print("WARNING: not replacing {}".format(ris))

        # if replacement csv provided, use rep_dict to update inj site names
        if replace_csv:

            cis = overlap_csv_meta_dct['Injection Site'].replace('_5', '').replace('_6a', '')
            overlap_csv_meta_dct['Injection Site'] = cis
            case_id = overlap_csv_meta_dct['Case Name']
            print("WARNING: Replacing {}, with {}".format(ris, overlap_csv_meta_dct['Injection Site']))

            channel = overlap_csv_meta_dct['Channel Number']
            key = "{}_{}".format(channel, case_id)
            if key in rep_dict:
                overlap_csv_meta_dct['Injection Site'] = "{}".format(
                    rep_dict[key].replace(' ', '_'))

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
            # Only interested in SC*_div{1,2,3,4} sections
            if division_regions and "_div" not in row['REGION']:
                continue
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


# returns dict with inj_name_chan_case_id: new_name items from csv
def replacement_csv_to_dict(csv_path):
    assert os.path.isfile(csv_path)

    with open(csv_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile)
        header_row_index = 4
        header_row = []
        rename_dict = {}
        # Read csv file with replacement names
        for row_index, row in enumerate(csvreader):
            if row_index > header_row_index:
                # If name change required
                if row[0] == 'yes':
                    # og_name = row[header_row.index('Original Name')].strip()
                    # og_name = og_name.replace("-", "_").lower()
                    case_id = row[header_row.index('Mouse Case ID')].strip()
                    channel = row[header_row.index('Channel')].strip()
                    new_name = row[header_row.index('Cortex Injection Site')].\
                        strip()
                    if '/' not in case_id:
                        # key = "{}_{}_{}".format(og_name, channel, case_id)
                        key = "{}_{}".format(channel, case_id)
                        assert key not in rename_dict
                        rename_dict[key] = new_name
                    else:
                        # if case_id has B/A suffix, used to signify two cases
                        # can potentially break if /C or more is added
                        first_id = case_id[:case_id.index('/')]
                        # key = "{}_{}_{}".format(og_name, channel, first_id)
                        key = "{}_{}".format(channel, first_id)
                        assert key not in rename_dict
                        rename_dict[key] = new_name

                        sec_id = first_id[:-1] + case_id[-1]
                        # key = "{}_{}_{}".format(og_name, channel, sec_id)
                        key = "{}_{}".format(channel, sec_id)
                        assert key not in rename_dict
                        rename_dict[key] = new_name
            # Read and save headings
            elif row_index == header_row_index:
                header_row = row

    return rename_dict


if __name__ == '__main__':
    main()
