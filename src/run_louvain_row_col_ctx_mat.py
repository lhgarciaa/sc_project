#!/usr/bin/env python
# Note: if not N x N will pad
from __future__ import print_function
import argparse
import csv
import os
import cPickle as pickle
from cic_dis import cic_utils
import bct
import time
import psutil
from multiprocessing import Pool


def main():
    parser = argparse.ArgumentParser(
        description="Runs Louvain modularity analysis on row source, column "
        " destination format CSV")
    parser.add_argument('-i', '--input_csv',
                        help='Input, labeled row source, column destination '
                        'annotation CSV',
                        required=True)
    parser.add_argument('-o', '--output_csv',
                        help='Output path for connectivity matrix csv',
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
    parser.add_argument('-wh', '--write_header',
                        help='Write header to file before first line(s)',
                        action="store_true")
    parser.add_argument('-und', '--undirected',
                        help='Specify input matrix as undirected',
                        action='store_true')

    args = vars(parser.parse_args())

    # get output path and related args first in case just checking for that
    gamma = float(args['gamma'])
    runs = int(args['runs'])
    verbose = args['verbose']
    input_csv_path = args['input_csv']
    output_csv_path = args['output_csv']
    print_output_path = args['print_output_path']
    if print_output_path:
        print("{}".format(output_csv_path))
        return 0

    # now check input path is actually valid
    assert os.path.isfile(input_csv_path),\
        "can't find input csv file {}".format(input_csv_path)

    num_slots = args['num_slots']
    write_header = args['write_header']
    undirected = args['undirected']

    # OPEN, READ INPUT CSV
    (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) = \
        cic_utils.read_ctx_mat(input_csv_path)

    assert len(col_roi_name_npa) == ctx_mat_npa.shape[1], \
        "ERROR length col_roi_name_npa {} != ctx_mat_npa cols {}". \
        format(len(col_roi_name_npa), ctx_mat_npa.shape[1])

    if verbose:
        print("{}".format(time.strftime("%m-%d-%Y %H:%M:%S", time.gmtime())))
        print("running louvain {} times using {} slots with gamma {}\non {}".
              format(runs, num_slots, gamma, input_csv_path))
        print("{} CPUs available".format(psutil.cpu_count()))

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
            cic_utils.conv_rect_ctx_mat_to_sq(
                row_roi_name_npa=row_roi_name_npa,
                col_roi_name_npa=col_roi_name_npa,
                ctx_mat_npa=ctx_mat_npa)
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
        map_arg_lst[idx] = (connectivity_matrix_npa, gamma, undirected,
                            verbose, num_slots)

    if verbose:
        print("done")

    # generate louvain run arr dict, format
    # [ { 'run' : run_index + 1,
    #     'num_communities' : len(community_structure_dict.keys(),
    #     'q' : q,
    #     'gamma' : gamma   # redundant but that's better than the alternative
    #     'community_structure' : community_structure_dict}, ... ]
    louvain_run_arr_dict = []

    if verbose:
        print("Calling Louvain with {} processes...".format(num_slots))
        start = time.time()

    map_results = []
    # call louvain
    # only do multi process thing if greater than 1 thread
    if num_slots > 1:
        #  first make process pool
        if verbose:
            print("Getting process pool...")
        pool = Pool(num_slots)
        if verbose:
            print("done")

        # map results in parallel
        map_results = pool.imap_unordered(modularity_louvain_dir_wrapper,
                                          map_arg_lst)

        # wait for work to finish
        pool.close()
        pool.join()

    # otherwise, use single process for call
    else:
        for map_arg in map_arg_lst:
            if undirected:
                map_results.append(bct.modularity_louvain_und(map_arg[0],
                                                              map_arg[1]))
            else:
                map_results.append(bct.modularity_louvain_dir(map_arg[0],
                                                              map_arg[1]))

    if verbose:
        print("done in {:0.06}s".format(time.time() - start))

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
    key_index_arr = sorted(
        louvain_run_arr_dict[0].keys(), reverse=True)
    # write louvain_run_arr_dict to output_csv_path
    assert len(louvain_run_arr_dict) > 0,\
        "Your louvain run ain't got no results bro"  # reasonable assumption

    if write_header:
        with open(output_csv_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile)
            # create key index automatically
            csvwriter.writerow(key_index_arr)
            for m in louvain_run_arr_dict:
                map_val_arr = []
                # follow keys defined in key_index_arr
                for key in key_index_arr:
                    map_val_arr.append(m[key])
                csvwriter.writerow(map_val_arr)

    else:
        with open(output_csv_path, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            for m in louvain_run_arr_dict:
                map_val_arr = []
                # follow keys defined in key_index_arr
                for key in key_index_arr:
                    map_val_arr.append(m[key])
                csvwriter.writerow(map_val_arr)

    print("Wrote Louvain results to {}".format(output_csv_path))

    output_pickle_path = cic_utils.pickle_path(output_csv_path)
    pickle.dump(args, open(output_pickle_path, "wb"))
    if verbose:
        print("Wrote pickle args to {}".format(output_pickle_path))

    if verbose:
        print("done at {}".format(
            time.strftime("%m-%d-%Y %H:%M:%S", time.gmtime())))


def modularity_louvain_dir_wrapper(args):
    # if verbose
    undirected = args[2]
    verbose = args[3]
    num_slots = args[4]
    p = psutil.Process()
    if verbose:
        print("calling modularity louvain dir at {}".format(
            time.strftime("%H:%M:%S", time.gmtime())))
        print("PID {}".format(p.pid))
        print("NUM SLOTS {}".format(num_slots))
        print("NUM CPUs {}".format(psutil.cpu_count()))
        print("original CPU affinity {}".format(p.cpu_affinity()))

    p.cpu_affinity(range(psutil.cpu_count()))
    if verbose:
        print("new CPU affinity {}".format(p.cpu_affinity()))

    only_mod_args = args[0:2]
    if undirected:
        return bct.modularity_louvain_und(*only_mod_args)
    else:
        return bct.modularity_louvain_dir(*only_mod_args)


if __name__ == "__main__":
    main()
