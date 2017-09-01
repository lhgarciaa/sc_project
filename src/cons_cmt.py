#!/usr/bin/env python
# just calculate consensus cmt str
from __future__ import print_function
import argparse
import csv
import os
import numpy as np
import cic_utils
import cic_ms
import sys

csv.field_size_limit(sys.maxsize)  # let's rock


def main():
    parser = argparse.ArgumentParser(description="Characterize repeated runs "
                                     "of community structure recorded in CSV")
    parser.add_argument('-i', '--input_csv',
                        help='Input, CSV containing multiple runs of '
                        'modularity detection', required=True)
    parser.add_argument('-lt', '--list_type',
                        help='Boolean true if community structure format is '
                        'list type',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
                        action='store_true')

    args = vars(parser.parse_args())

    input_csv_path = args['input_csv']
    assert os.path.isfile(input_csv_path),\
        "can't find input csv file {}".format(input_csv_path)
    list_type = args['list_type']
    verbose = args['verbose']

    # parse input csv into louvain run arr dict, all values are strings
    # [ { 'run' : run
    #     'num_communities' : num_communities
    #     'q' : q,
    #     'gamma' : gamma   # redundant but that's better than the alternative
    #     'community_structure' : community_structure_dict string}, ... ]

    if verbose:
        print("Reading Louvain output CSV")
        import time
        start = time.time()
    louvain_run_arr_dict = cic_utils.read_louvain_run_arr_dict(input_csv_path)

    if verbose:
        print("done in {}s".format(time.time()-start))

    if verbose:
        print("Converting format of read louvain run arr dict")
        import time
        start = time.time()

    run_npa = np.array([x['run'] for x in louvain_run_arr_dict])

    # make set of sets from each community_structure and tally count of each
    com_cnt_dict = {}  # { community_structure_set_of_sets : count }
    cmt_str_lst_fs_fs = []  # community structure list, list
    roi_name_lst = []
    for run in louvain_run_arr_dict:
        if list_type:
            cmt_str_lst = run['community_structure']
        else:
            cmt_str_lst = run['community_structure'].values()

        roi_name_lst = sorted(cic_utils.flatten(cmt_str_lst))

        cmt_str_lst_fs_fs.append(cic_ms.lst_lst_to_fs_fs(cmt_str_lst))
        set_of_sets = frozenset([frozenset(x) for x in cmt_str_lst])
        cnt = com_cnt_dict.get(set_of_sets, 0)
        com_cnt_dict[set_of_sets] = cnt + 1

    if verbose:
        print("done in {}s".format(time.time()-start))

    num_runs = np.max(run_npa)
    # calculate consensus community structure
    if verbose:
        print("calculating cons_cmt_str...")
        start = time.time()
    cons_cmt_str = cic_ms.calc_cons_cmt_str(
        roi_name_lst=roi_name_lst,
        cmt_str_lst_fs_fs=cmt_str_lst_fs_fs,
        gamma=louvain_run_arr_dict[0]['gamma'],
        runs=num_runs,
        tau=0.1)
    if verbose:
        print("done in {}s".format(time.time()-start))

    assert len(louvain_run_arr_dict) > 0  # reasonable assumption i hope

    # write to std out in csv file format
    csvwriter = csv.writer(sys.stdout)

    # now write community structure values
    row = []
    row.append('consensus com str:')
    # convert to lst_lst to save space in csv
    cons_cmt_str_lst_lst = cic_ms.fs_fs_to_lst_lst(cons_cmt_str)
    row.append(cons_cmt_str_lst_lst)
    csvwriter.writerow(row)


if __name__ == "__main__":
    main()
