#!/usr/bin/env python
# Note: if not N x N will pad
from __future__ import print_function
import argparse
import csv
import os
import cPickle as pickle
import cic_utils
import bct
import time
from multiprocessing.dummy import Pool as ThreadPool


def main():
    parser = argparse.ArgumentParser(
        description="Runs Louvain modularity analysis on row source, column "
        " destination format CSV")
    parser.add_argument('-i', '--input_csv',
                        help='Input, labeled row source, column destination '
                        'annotation CSV',
                        required=True)
    parser.add_argument('-g', '--gamma', help='Louvain gamma value',
                        required=True)
    parser.add_argument('-r', '--runs', help='Number of times to run Louvain',
                        required=True)
    parser.add_argument('-v', '--verbose',
                        help='Print relevant but optional output',
                        action='store_true')
    parser.add_argument('-pop', '--print_output_path',
                        help='Simply print output path and quit',
                        action='store_true')
    parser.add_argument('-ns', '--num_slots',
                        help='Number of slots to use for SMP',
                        type=int, default=1)

    args = vars(parser.parse_args())

    # get output path and related args first in case just checking for that
    gamma = float(args['gamma'])
    runs = int(args['runs'])
    verbose = args['verbose']
    input_csv_path = args['input_csv']
    name_of_study = input_csv_path.replace(".csv", "")
    output_csv_path = "{}_gamma-{:.2f}_runs-{:04d}.csv".\
        format(name_of_study, gamma, runs)
    print_output_path = args['print_output_path']
    if print_output_path:
        print("{}".format(output_csv_path))
        return 0

    # now check input path is actually valid
    assert os.path.isfile(input_csv_path),\
        "can't find input csv file {}".format(input_csv_path)

    num_slots = args['num_slots']

    # OPEN, READ INPUT CSV
    (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) = \
        cic_utils.read_ctx_mat(input_csv_path)

    if verbose:
        print("{}".format(time.strftime("%m-%d-%Y %H:%M:%S", time.gmtime())))
        print("running louvain {} times using {} slots with gamma {}\non {}".
              format(runs, num_slots, gamma, input_csv_path))

    # double check formatting, shape of array
    if cic_utils.is_sq(row_roi_name_npa=row_roi_name_npa,
                       col_roi_name_npa=col_roi_name_npa,
                       ctx_mat_npa=ctx_mat_npa):
        roi_name_npa = row_roi_name_npa
        sq_ctx_mat_npa = ctx_mat_npa

    else:  # else if not square, then either pad or convert
        if verbose:
            shape = ctx_mat_npa.shape
            print("matrix in is not square\nrows/cols {}/{}".format(
                shape[0], shape[1]))
            print("and/or row ROIs don't match col ROIs")

        if verbose:
            print("converting to square...")
            start = time.time()
        (sq_roi_name_npa, sq_ctx_mat_npa) = \
            cic_utils.conv_rect_ctx_mat_to_sq(row_roi_name_npa,
                                              col_roi_name_npa,
                                              ctx_mat_npa)
        roi_name_npa = sq_roi_name_npa
        if verbose:
            shape = sq_ctx_mat_npa.shape
            print("done in {:.02}s\nnew rows/cols {}/{}".format(
                time.time()-start, shape[0], shape[1]))

    connectivity_matrix_npa = sq_ctx_mat_npa

    # check for capitlization/duplicates
    cic_utils.dup_check_container(dup_check_roi_container=roi_name_npa,
                                  input_csv_path=input_csv_path)

    if verbose:
        print("Preparing Louvain arguments...")

    # call multithreaded louvain
    # first create argument list
    map_arg_lst = [(None, None)] * runs
    for idx in xrange(runs):
        map_arg_lst[idx] = (connectivity_matrix_npa, gamma)

    if verbose:
        print("done")

    # generate louvain run arr dict, format
    # [ { 'run' : run_index + 1,
    #     'num_communities' : len(community_structure_dict.keys(),
    #     'q' : q,
    #     'gamma' : gamma   # redundant but that's better than the alternative
    #     'community_structure' : community_structure_dict}, ... ]
    louvain_run_arr_dict = []

    # call louvain
    #  first make threads
    pool = ThreadPool(num_slots)
    if verbose:
        print("Calling Louvain with {} threads...".format(num_slots))
        start = time.time()

    # map results in parallel
    map_results = pool.map(modularity_louvain_dir_wrapper, map_arg_lst)

    # wait for work to finish
    pool.close()
    pool.join()

    if verbose:
        print("done in {:.02}s".format(time.time() - start))

    # march through results and write to CSV
    for result_idx, map_result in enumerate(map_results):
        (ci, q) = map_result

        assert len(ci) == roi_name_npa.size,\
            "Uh-oh, found commmunities don't make sense"

        community_structure_dict = cic_utils.build_community_structure_dict(
            ci=ci,
            roi_name_npa=roi_name_npa)

        # create wrapper dict for community structure dict
        louvain_run_dict = cic_utils.build_louvain_run_dict(
            run_index=result_idx,
            q=q,
            community_structure_dict=community_structure_dict,
            gamma=gamma)

        louvain_run_arr_dict.append(louvain_run_dict)

    # WRITE LOUVAIN TO OUTPUT CSV
    # write louvain_run_arr_dict to output_csv_path
    assert len(louvain_run_arr_dict) > 0,\
        "Your louvain run ain't got no results bro"  # reasonable assumption
    with open(output_csv_path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        # create key index automatically
        key_index_arr = sorted(louvain_run_arr_dict[0].keys(), reverse=True)
        csvwriter.writerow(key_index_arr)

        for m in louvain_run_arr_dict:
            map_val_arr = []
            # follow keys defined in key_index_arr
            for key in key_index_arr:
                map_val_arr.append(m[key])

            csvwriter.writerow(map_val_arr)

        print("Wrote Louvain results to {}".format(output_csv_path))

        output_pickle_path = cic_utils.pickle_path(output_csv_path)
        if verbose:
            print("Wrote pickle args to {}".format(output_pickle_path))
        pickle.dump(args, open(output_pickle_path, "wb"))


def modularity_louvain_dir_wrapper(args):
    return bct.modularity_louvain_dir(*args)


if __name__ == "__main__":
    main()
