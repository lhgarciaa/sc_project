#!/usr/bin/env python
# if not N x N will pad
from __future__ import print_function
import argparse
import csv
import os
import numpy as np
from cic_dis import cic_utils
from cic_dis import cic_ms
from cic_dis import cic_plot
import sys

csv.field_size_limit(sys.maxsize)  # let's rock


def main():
    parser = argparse.ArgumentParser(description="Characterize repeated runs "
                                     "of community structure recorded in CSV")
    parser.add_argument('-i', '--input_csv',
                        help='Input, CSV containing multiple runs of '
                        'modularity detection', required=True)
    parser.add_argument('-H', '--header',
                        help='Include header info, typically used first write',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
                        action='store_true')

    args = vars(parser.parse_args())

    input_csv_path = args['input_csv']
    assert os.path.isfile(input_csv_path),\
        "can't find input csv file {}".format(input_csv_path)
    display_header = args['header']
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

    num_com_npa = np.array(
        [x['num_communities'] for x in louvain_run_arr_dict])
    q_npa = np.array([x['q'] for x in louvain_run_arr_dict])

    # make set of sets from each community_structure and tally count of each
    com_cnt_dict = {}  # { community_structure_set_of_sets : count }
    cmt_str_lst_fs_fs = []  # community structure list, list
    roi_name_lst = []
    for run in louvain_run_arr_dict:
        if len(roi_name_lst) == 0:
            roi_name_lst = sorted(
                cic_utils.flatten(run['community_structure'].values()))

        cmt_str_lst = run['community_structure'].values()
        cmt_str_lst_fs_fs.append(cic_ms.lst_lst_to_fs_fs(cmt_str_lst))
        set_of_sets = frozenset([frozenset(x) for x in cmt_str_lst])
        cnt = com_cnt_dict.get(set_of_sets, 0)
        com_cnt_dict[set_of_sets] = cnt + 1

    if verbose:
        print("done in {}s".format(time.time()-start))

    # calculate a bunch of metrics
    num_runs = len(louvain_run_arr_dict)
    q_max = np.max(q_npa)
    unique_cmt_str = len(com_cnt_dict.keys())
    cmt_str_cnt_npa = np.array([x for x in com_cnt_dict.values()])
    cmt_str_mode_count = np.max(cmt_str_cnt_npa)
    # multi-scale stuff
    res_dct = {}
    if verbose:
        print("calculating std_dev_w_alpha_beta...")
        start = time.time()
    std_dev_w_alpha_beta = cic_ms.calc_std_w_alpha_beta(
        roi_name_lst=roi_name_lst, cmt_str_lst_fs_fs=cmt_str_lst_fs_fs,
        res_dct=res_dct)
    if verbose:
        print("done in {}s: {}".format(
            time.time()-start,
            std_dev_w_alpha_beta)
        )

    if verbose:
        print("calculating mean_var_z_alpha_beta...")
        start = time.time()
    mean_var = cic_ms.calc_mean_var_z_alpha_beta(
        roi_name_lst=roi_name_lst,
        std_w_alpha_beta=std_dev_w_alpha_beta,
        cmt_str_lst_fs_fs=cmt_str_lst_fs_fs,
        M=cic_ms.n_choose_2(len(cmt_str_lst_fs_fs)),
        res_dct=res_dct)
    if verbose:
        print("done in {}s: {}".format(
            time.time()-start,
            mean_var)
        )

    qmax_cmt_str = []
    for run in louvain_run_arr_dict:
        if len(qmax_cmt_str) == 0 and run['q'] == q_max:
            qmax_cmt_str = sorted(run['community_structure'].values())

    # okay phew! now calculate consensus community structure
    if verbose:
        print("calculating cons_cmt_str...")
        start = time.time()
    if std_dev_w_alpha_beta == 0 or mean_var == float('Inf'):
        if verbose:
            print("No st.dev, returning arbitrary cmt str as consensus")
        cons_cmt_str = next(iter(cmt_str_lst_fs_fs))
    else:
        cons_cmt_str = cic_ms.calc_cons_cmt_str(
            roi_name_lst=roi_name_lst,
            cmt_str_lst_fs_fs=cmt_str_lst_fs_fs,
            gamma=louvain_run_arr_dict[0]['gamma'],
            runs=num_runs,
            tau=0.1)
    if verbose:
        print("done in {}s".format(time.time()-start))

    assert len(louvain_run_arr_dict) > 0  # reasonable assumption i hope

    # create print dict to be written to csv as single row
    #  note no cmt structure included due to size limitations
    print_dict = {}
    print_dict[(0, 'num runs')] = num_runs
    print_dict[(0.5, 'gamma')] = louvain_run_arr_dict[0]['gamma']
    print_dict[(0.6, 'mean part sim')] = mean_var[0]
    print_dict[(0.7, 'var part sim')] = mean_var[1]
    print_dict[(0.8, 'len con cmt str')] = len(cons_cmt_str)
    print_dict[(1, 'max num com')] = np.max(num_com_npa)
    print_dict[(2, 'mean num com')] = np.mean(num_com_npa)
    print_dict[(3, 'std dev num com')] = np.std(num_com_npa)
    print_dict[(4, 'max q')] = q_max
    print_dict[(5, 'mean q')] = np.mean(q_npa)
    print_dict[(6, 'std dev')] = np.std(q_npa)
    print_dict[(7, 'unique cmt str')] = "{}/{}".format(
        unique_cmt_str,
        num_runs)
    print_dict[(8, 'cmt str mode count')] = "{}/{}".\
        format(cmt_str_mode_count.tolist(), num_runs)

    # write to std out in csv file format
    csvwriter = csv.writer(sys.stdout)

    if display_header:
        row = []
        for key in sorted(print_dict.keys()):
            row.append(key[1])
        csvwriter.writerow(row)

    row = []
    for key in sorted(print_dict.keys()):
        row.append(print_dict[key])
    csvwriter.writerow(row)

    # now write community structure values
    row = []
    row.append('consensus cmt str:')
    # convert to lst_lst to save space in csv
    cons_cmt_str_lst_lst = cic_ms.fs_fs_to_lst_lst(cons_cmt_str)
    row.append(cons_cmt_str_lst_lst)
    csvwriter.writerow(row)
    row = []
    row.append('consensus cmt inj sites:')
    cmt_inj_sites = cic_plot.cmt_inj_site_lst_from_cons_cmt_str(
        cons_cmt_str_lst_lst)
    row.append(cmt_inj_sites)
    csvwriter.writerow(row)


if __name__ == "__main__":
    main()
