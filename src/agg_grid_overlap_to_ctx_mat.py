#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
from cic_dis import cic_overlap
import cPickle as pickle
import csv
from cic_dis import cic_utils
import sys
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(
        description="Converts aggregated overlap output to connectivity "
        "matrix csv")
    parser.add_argument('-i', '--input_agg_overlap_csv',
                        help='Input aggregated overlap csv',
                        required=True)
    parser.add_argument('-o', '--output_ctx_mat_csv',
                        help='Output path for connectivity matrix csv',
                        required=True)
    parser.add_argument('-hemi', '--hemisphere_of_interest',
                        help='exclusively include listed hemisphere in output')
    parser.add_argument('-es', '--exclude_sections',
                        help='List of case:section tuples to exclude from '
                        'ctx mat e.g. -es SW130212-02A:1_09 SW160212-02A:1_10',
                        nargs='+')
    parser.add_argument('-v', '--verbose',
                        help='Print extra information about conversion',
                        action='store_true')

    # READ ARGS
    args = vars(parser.parse_args())

    input_agg_overlap_csv = args['input_agg_overlap_csv']
    output_ctx_mat_csv = args['output_ctx_mat_csv']
    verbose = args['verbose']
    hemisphere_of_interest = args['hemisphere_of_interest']
    check_hemi = hemisphere_of_interest is not None
    exclude_sections = args['exclude_sections']

    assert os.path.isfile(input_agg_overlap_csv), "{} not found".\
        format(input_agg_overlap_csv)

    (agg_overlap_csv_header, agg_overlap_rows) = \
        cic_overlap.read_agg_overlap_csv(input_csv_path=input_agg_overlap_csv)

    cell_lbl_set = frozenset()
    inj_site_lbl_set = frozenset()

    # for managing extents
    curr_ara_level = -1
    # keep track of overlap for each injection site
    inj_site_overlap_dcts = defaultdict(lambda: defaultdict())

    if verbose:
        print("Calculating connectivity matrix from {} agg overlap rows".
              format(len(agg_overlap_rows)))
        if exclude_sections is not None:
            print("Excluding {} sections: {}".format(len(exclude_sections),
                                                     exclude_sections))

    for row_idx, row in enumerate(agg_overlap_rows):
        # get constant vals, assume
        # Atlas Name, Atlas Version, Channel Number, Grid Size, Overlap Format
        #   Tracer are the same for all rows
        if row_idx == 0:
            ATLAS_NAME = row[agg_overlap_csv_header.index('Atlas Name')]
            ATLAS_VERSION = row[agg_overlap_csv_header.index('Atlas Version')]
            GRID_SIZE = int(row[agg_overlap_csv_header.index('Grid Size')])
            OVERLAP_FORMAT = row[agg_overlap_csv_header.index(
                'Overlap Format')]

        # march through rows
        # for assertion
        atlas_name = row[agg_overlap_csv_header.index('Atlas Name')]
        atlas_version = row[agg_overlap_csv_header.index('Atlas Version')]
        grid_size = int(row[agg_overlap_csv_header.index('Grid Size')])
        overlap_format = row[agg_overlap_csv_header.index(
            'Overlap Format')]
        tracer = row[agg_overlap_csv_header.index('Tracer')]
        # get section and case in event exclude_sections list provided
        section = row[agg_overlap_csv_header.index('Slide Number')]
        case = row[agg_overlap_csv_header.index('Case Name')]

        # assert these are always the same
        #   Atlas Name, Atlas Version, Channel Number, Grid Size, Overlap
        # Format
        assert atlas_name == ATLAS_NAME
        assert atlas_version == ATLAS_VERSION
        assert grid_size == GRID_SIZE
        assert overlap_format == OVERLAP_FORMAT

        # set antero or retro mode based on tracer
        tracer_type = 'antero'  # assume antero
        if 'ctb' in tracer.lower() or 'fg' in tracer.lower():
            tracer_type = 'retro'

        # moving values
        ara_level = int(row[agg_overlap_csv_header.index('ARA Level')])
        hemi_col_row = row[agg_overlap_csv_header.
                           index('(HEMISPHERE:COLUMN:ROW)')]
        hemi = hemi_col_row.split(':')[0].replace('(', '')
        col_num = int(hemi_col_row.split(':')[1])
        row_num = int(hemi_col_row.split(':')[2].replace(')', ''))

        if ara_level != curr_ara_level:
            curr_ara_level = ara_level
            # keep record of extents for sanity check
            max_ext = {'l': {'row': 0, 'col': 0}, 'r': {'row': 0, 'col': 0}}
            min_ext = {'l': {'row': sys.maxint, 'col': sys.maxint},
                       'r': {'row': sys.maxint, 'col': sys.maxint}}

        # update extents for sanity check
        if col_num > max_ext[hemi]['col']:
            max_ext[hemi]['col'] = col_num
        if row_num > max_ext[hemi]['row']:
            max_ext[hemi]['row'] = row_num
        if col_num < min_ext[hemi]['col']:
            min_ext[hemi]['col'] = col_num
        if row_num < min_ext[hemi]['row']:
            min_ext[hemi]['row'] = row_num

        inj_site = row[agg_overlap_csv_header.index('Injection Site')]
        grid_only = int(row[agg_overlap_csv_header.index('GRID ONLY')])
        overlap = int(row[agg_overlap_csv_header.index('OVERLAP')])

        # assert GRID ONLY + OVERLAP == Grid Size**2
        assert grid_only + overlap == grid_size ** 2 \
            or col_num == max_ext[hemi]['col'] \
            or row_num == max_ext[hemi]['row'] \
            or col_num == min_ext[hemi]['col'] \
            or row_num == min_ext[hemi]['row'],\
            'line {}\ncol/min_col/max_col {}/{}/{}\n'\
            'row/min_row/max_row {}/{}/{}\n'\
            'grid only {}, overlap {}, grid_size {}'.\
            format(row_idx + 2,
                   col_num, min_ext[hemi]['col'], max_ext[hemi]['col'],
                   row_num, min_ext[hemi]['row'], max_ext[hemi]['row'],
                   grid_only, overlap, grid_size)

        # only make and add lbl to dct if hemi of interest or not checking hemi
        if (not check_hemi or hemi == hemisphere_of_interest) and \
           (not exclude_sections or
                "{}:{}".format(case, section) not in exclude_sections):
            # first make (ara_level:hemi:col:row) cell label
            cell_lbl = "({}:{})".format(ara_level, hemi_col_row.
                                        replace('(', '').replace(')', ''))

            # TODO change inj_site and other terminology to src vs. dest
            # build labels and dct lst
            # if antero
            if tracer_type == 'antero':
                # cell labels from all (HEMISPHERE:COLUMN:ROWS) values
                cell_lbl_set = cell_lbl_set.union(frozenset({cell_lbl}))
                #   injection site labels from all Injection Site values
                inj_site_lbl_set = inj_site_lbl_set.union(
                    frozenset({inj_site}))
            elif tracer_type == 'retro':
                # cell labels from all inj_site values
                cell_lbl_set = cell_lbl_set.union(frozenset({inj_site}))
                #   injection site labels from all Injection Site values
                inj_site_lbl_set = inj_site_lbl_set.union(
                    frozenset({cell_lbl}))
            else:
                assert 0, 'Tracer type should either be antro or retro'

            #   populate dcts
            #     { 'Injection Site' : '...' {cell_lbl1 : (grid_only,overlap),
            #                                 cell_lbl2 : ...} }
            if tracer_type == 'antero':
                inj_site_overlap_dct = \
                                       inj_site_overlap_dcts[inj_site]
                overlap_tup = inj_site_overlap_dct.get(cell_lbl, (0, 0))
                overlap_tup = tuple(
                    map(lambda x, y: x + y, overlap_tup, (grid_only, overlap)))

                inj_site_overlap_dct[cell_lbl] = overlap_tup

            else:
                inj_site_overlap_dct = \
                                       inj_site_overlap_dcts[cell_lbl]
                overlap_tup = inj_site_overlap_dct.get(inj_site, (0, 0))
                overlap_tup = tuple(
                    map(lambda x, y: x + y, overlap_tup, (grid_only, overlap)))

                inj_site_overlap_dct[inj_site] = overlap_tup

        pct_str = "\r{0:0.2f}% complete... ".\
                  format((float(row_idx)/float(len(agg_overlap_rows)))*100.0)
        print(pct_str, end='')

    # fill all rows with dct lst, need initial blank for header
    cell_lbls = [''] + sorted(cell_lbl_set, key=cell_lbl_to_tup)
    inj_site_lbls = sorted(inj_site_lbl_set)
    with open(output_ctx_mat_csv, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(cell_lbls)
        for inj_site_lbl in inj_site_lbls:
            cols = [inj_site_lbl]
            for cell_lbl in cell_lbls[1:len(cell_lbls)]:
                # do get to make sure cell_lbl exists for given injection site
                overlap_tup = inj_site_overlap_dcts[inj_site_lbl].get(cell_lbl)
                if overlap_tup is not None and len(overlap_tup) > 0:
                    assert len(overlap_tup) == 2, \
                        "overlap tup: {}".format(overlap_tup)
                    grid_only = overlap_tup[0]
                    overlap = overlap_tup[1]
                    cols.append(float(overlap)/float(grid_only + overlap))
                else:
                    cols.append('')
            csvwriter.writerow(cols)  # string technically a sequence

    pct_str = "\r{0:0.2f}% complete... ".format(100)
    print(pct_str)

    output_pickle_path = cic_utils.pickle_path(output_ctx_mat_csv)
    pickle_dct = cic_utils.pickle_dct(args)
    pickle.dump(pickle_dct, open(output_pickle_path, "wb"))


def cell_lbl_to_tup(lbl):
    lst = lbl.replace('(', '').replace(')', '').split(':')
    # if grid label
    if len(lst) > 1:
        return tuple([(x == 'r' or x == 'l') and x or int(x) for x in lst])
    # else inj site label
    else:
        return tuple(lbl)


if __name__ == '__main__':
    main()
