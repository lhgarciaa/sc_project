#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
from cic_dis import cic_overlap
import cPickle as pickle
import csv
from cic_dis import cic_utils
from collections import defaultdict
import re


def main():
    parser = argparse.ArgumentParser(
        description="Converts aggregated overlap output to connectivity "
        "matrix csv")
    parser.add_argument('-ant_i', '--ant_input_agg_overlap_csv',
                        help='Input aggregated overlap csv',
                        required=True)
    parser.add_argument('-ret_i', '--ret_input_agg_overlap_csv',
                        help='Input aggregated overlap csv',
                        required=True)
    parser.add_argument('-o', '--output_ctx_mat_csv',
                        help='Output path for connectivity matrix csv',
                        required=True)
    parser.add_argument('-hemi', '--hemisphere_of_interest',
                        help='exclusively include listed hemisphere in output')
    parser.add_argument('-mtv', '--minimum_threshold_value',
                        help='Only write cols with values over particular min',
                        required=False,
                        type=float,
                        default=0.0)
    parser.add_argument('-eir', '--exclusively_include_rois',
                        help='A list of ROIS to include... exclusively',
                        nargs='+')
    parser.add_argument('-es', '--exclude_sections',
                        help='List of case:section tuples to exclude from '
                        'ctx mat e.g. -es SW130212-02A:1_09 SW160212-02A:1_10',
                        nargs='+')
    parser.add_argument('-v', '--verbose',
                        help='Print extra information about conversion',
                        action='store_true')

    # READ ARGS
    args = vars(parser.parse_args())

    ant_input_agg_overlap_csv = args['ant_input_agg_overlap_csv']
    ret_input_agg_overlap_csv = args['ret_input_agg_overlap_csv']
    output_ctx_mat_csv = args['output_ctx_mat_csv']
    verbose = args['verbose']
    hemisphere_of_interest = args['hemisphere_of_interest']
    check_hemi = hemisphere_of_interest is not None
    exclude_sections = args['exclude_sections']
    eir = args['exclusively_include_rois']
    mtv = args['minimum_threshold_value']

    ant_src_lbls = []
    ret_src_lbls = []
    ant_dst_lbls = []
    ret_dst_lbls = []

    # for managing extents
    # keep track of overlap for each injection site
    ant_inj_site_overlap_dcts = defaultdict(lambda: defaultdict())
    ret_inj_site_overlap_dcts = defaultdict(lambda: defaultdict())

    # Repeat the process twice, once for each tracer type
    for input_agg_overlap_csv in [ant_input_agg_overlap_csv,
                                  ret_input_agg_overlap_csv]:
        tracer_mode = \
            "retrograde" if 'ret' in input_agg_overlap_csv else "anterograde"

        if verbose:
            print("Using tracer mode {}".format(tracer_mode))

        assert os.path.isfile(input_agg_overlap_csv), "{} not found".\
            format(input_agg_overlap_csv)

        (agg_overlap_csv_header, agg_overlap_rows) = \
            cic_overlap.read_agg_overlap_csv(
                input_csv_path=input_agg_overlap_csv)

        dst_lbl_set = frozenset()
        src_lbl_set = frozenset()

        if verbose:
            print("Calculating connectivity matrix from {} agg overlap rows".
                  format(len(agg_overlap_rows)))
            if exclude_sections is not None:
                print("Excluding {} sections: {}".format(len(exclude_sections),
                                                         exclude_sections))
            if eir is not None:
                print("Including only {} sections: {}".format(len(eir), eir))

        for row_idx, row in enumerate(agg_overlap_rows):
            # get constant vals, assume
            # Atlas Name, Atlas Version, Channel Number,
            # Grid Size, Overlap Format
            # Tracer are the same for all rows
            if row_idx == 0:
                ATLAS_NAME = row[agg_overlap_csv_header.index('Atlas Name')]
                ATLAS_VERSION = row[agg_overlap_csv_header.index(
                    'Atlas Version')]
                OVERLAP_FORMAT = row[agg_overlap_csv_header.index(
                    'Overlap Format')]
                assert OVERLAP_FORMAT == 'Region'

            # march through rows
            # for assertion
            atlas_name = row[agg_overlap_csv_header.index('Atlas Name')]
            atlas_version = row[agg_overlap_csv_header.index('Atlas Version')]
            assert 'Grid Size' not in agg_overlap_csv_header
            overlap_format = row[agg_overlap_csv_header.index(
                'Overlap Format')]
            # get section and case in event exclude_sections list provided
            section = row[agg_overlap_csv_header.index('Slide Number')]
            case = row[agg_overlap_csv_header.index('Case Name')]

            # assert these are always the same
            #   Atlas Name, Atlas Version, Channel Number, Grid Size, Overlap
            # Format
            assert atlas_name == ATLAS_NAME
            assert atlas_version == ATLAS_VERSION, \
                "{} does not equal {}".format(atlas_version, ATLAS_VERSION)
            assert overlap_format == OVERLAP_FORMAT

            inj_site = row[agg_overlap_csv_header.index('Injection Site')]
            overlap = int(row[agg_overlap_csv_header.index('OVERLAP')])

            # Need to support overlap data without hemisphere included
            #  if is included then set hemi normally
            if '(HEMISPHERE:R:G:B)' in agg_overlap_csv_header:
                hemi_etc = row[agg_overlap_csv_header.index(
                    '(HEMISPHERE:R:G:B)')]
                hemi = hemi_etc.split(':')[0].replace('(', '')
            #  else if no hemi included then set hemi to None
            elif 'REGION RGB' in agg_overlap_csv_header:
                hemi = None
            else:
                assert None, "invalid overlap format"

            roi = row[agg_overlap_csv_header.index('REGION')]
            source_only = int(row[agg_overlap_csv_header.index('ATLAS ONLY')])

            # only make and add lbl to dct if mtv overlap present and
            #  hemi of interest or not checking hemi and
            #  not excluding sections or section not excluded
            #  not roi exclusive or roi included
            if ((not check_hemi or hemi == hemisphere_of_interest) and
                (not exclude_sections or
                 "{}:{}".format(case, section) not in exclude_sections) and
                (not eir or
                 len([r for r in eir if
                      r == roi or
                      re.search(
                          '^' + r + '[a-z0-9_]', roi) is not None]) > 0)):
                # ^^^ check for exact match e.g. VISal_2/3 or == VISal_2/3
                # or that e.g. MO matches MOp but not MOB ^^^
                # first make 'roi' cell label
                roi_lbl = "{}".format(roi)

                # TODO change inj_site and other terminology to src vs. dest
                # build labels and dct lst
                # if anterograde
                if tracer_mode == 'anterograde':
                    # cell labels from all (HEMISPHERE:COLUMN:ROWS) values
                    dst_lbl_set = dst_lbl_set.union(frozenset({roi_lbl}))
                    #   injection site labels from all Injection Site values
                    src_lbl_set = src_lbl_set.union(
                        frozenset({inj_site}))
                elif tracer_mode == 'retrograde':
                    # cell labels from all inj_site values
                    dst_lbl_set = dst_lbl_set.union(frozenset({inj_site}))
                    #   injection site labels from all Injection Site values
                    src_lbl_set = src_lbl_set.union(
                        frozenset({roi_lbl}))
                else:
                    assert 0, 'Tracer type should either be antro or ' \
                              'retrograde'

                # populate dcts
                #  antero
                #  { 'Injection Site' : '...'{roi_lbl1: (source_only, overlap),
                #                              roi_lbl2 : ...} }
                if tracer_mode == 'anterograde':
                    inj_site_overlap_dct = \
                                           ant_inj_site_overlap_dcts[inj_site]
                    overlap_tup = inj_site_overlap_dct.get(roi_lbl, (0, 0))
                    overlap_tup = tuple(map(lambda x, y: x + y, overlap_tup,
                                            (source_only, overlap)))

                    inj_site_overlap_dct[roi_lbl] = overlap_tup
                #  retro
                #  { 'Roi label' : '...' {inj_site1 : (source_only, overlap),
                #                         inj_site2 : ...} }
                else:
                    inj_site_overlap_dct = \
                                           ret_inj_site_overlap_dcts[roi_lbl]
                    overlap_tup = inj_site_overlap_dct.get(inj_site, (0, 0))
                    overlap_tup = tuple(
                        map(lambda x, y: x + y, overlap_tup,
                            (source_only, overlap)))

                    inj_site_overlap_dct[inj_site] = overlap_tup

            pct_str = "\r{0:0.2f}% complete... ".format(
                (float(row_idx)/float(len(agg_overlap_rows)))*100.0)
            print(pct_str, end='')

        # define max overlap for each ROI
        max_roi_olp_dct = defaultdict(float)

        if tracer_mode == 'anterograde':

            for inj_site in ant_inj_site_overlap_dcts:
                for roi in ant_inj_site_overlap_dcts[inj_site]:
                    overlap_tup = ant_inj_site_overlap_dcts[inj_site][roi]
                    source_only = overlap_tup[0]
                    overlap = overlap_tup[1]
                    max_roi_olp_dct[roi] = max(
                        max_roi_olp_dct[roi],
                        mat_olp_calc(source_only=source_only, overlap=overlap))

        else:  # retrograde
            for roi in ret_inj_site_overlap_dcts:
                for inj_site in ret_inj_site_overlap_dcts[roi]:
                    overlap_tup = ret_inj_site_overlap_dcts[roi][inj_site]
                    source_only = overlap_tup[0]
                    overlap = overlap_tup[1]
                    max_roi_olp_dct[roi] = max(
                        max_roi_olp_dct[roi],
                        overlap)

        # only get labels with > max intensity, ant case these are output rois

        if tracer_mode == 'anterograde':

            ant_src_lbls = sorted(src_lbl_set)
            ant_dst_lbls += sorted([lbl for lbl in dst_lbl_set if
                                    max_roi_olp_dct[lbl] > mtv])

            if verbose:
                print("Filtered\n{} with mtv {}...".format(
                    sorted(dst_lbl_set), mtv))
                print("result\n{}".format(ant_dst_lbls[1:len(ant_dst_lbls)]))

        else:  # retrograde
            ret_src_lbls = sorted([lbl for lbl in src_lbl_set if
                                   max_roi_olp_dct[lbl] > mtv])
            ret_dst_lbls = sorted(dst_lbl_set)

            if verbose:
                print("Filtered\n{} with mtv {}...".format(
                    sorted(src_lbl_set), mtv))
                print("result\n{}".format(ret_src_lbls[1:len(ret_src_lbls)]))

    # Get complete list of src and dst lbls
    src_lbls = ant_src_lbls + ret_src_lbls
    dst_lbls = ant_dst_lbls + ret_dst_lbls

    # Get union of both src and dst lbls
    src_lbls = list(set(filter(lambda x: x in dst_lbls, src_lbls)))
    dst_lbls = list(set(filter(lambda x: x in src_lbls, dst_lbls)))

    assert len(src_lbls) == len(dst_lbls), "Should be equal number of labels"

    # fill all rows with dct lst, need initial blank for headers
    with open(output_ctx_mat_csv, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Sort source and destination lbls
        src_lbls = sorted(src_lbls)
        dst_lbls = sorted(dst_lbls)

        # Add leading space to dst_lbls and write as first row
        dst_lbls = [''] + dst_lbls
        csvwriter.writerow(dst_lbls)

        for src_lbl in src_lbls:
            cols = [src_lbl]

            # See if src_lbls is in ant_src_lbls
            if src_lbl in ant_src_lbls:
                inj_site_overlap_dct = ant_inj_site_overlap_dcts[src_lbl]
            else:
                inj_site_overlap_dct = ret_inj_site_overlap_dcts[src_lbl]

            if verbose:
                print("read inj site ovlp dct for {}, length {}".
                      format(src_lbl, len(inj_site_overlap_dct)))
            for dst_lbl in dst_lbls[1:len(dst_lbls)]:

                overlap_tup = inj_site_overlap_dct.get(dst_lbl, None)
                # do get to make sure dst_lbl exists for given injection site
                if verbose:
                    if overlap_tup is None:
                        print("no overlap tup for {}, {}".
                              format(src_lbl, dst_lbl))

                if overlap_tup is not None and len(overlap_tup) > 0:
                    assert len(overlap_tup) == 2, \
                        "overlap tup: {}".format(overlap_tup)
                    source_only = overlap_tup[0]
                    overlap = overlap_tup[1]
                    assert source_only + overlap > 0, \
                        "WARNING: cell {} has no source or overlap".format(
                                dst_lbl)
                    if src_lbl in ant_src_lbls:
                        # Checking if labeling also present retrograde
                        rec_dct = ret_inj_site_overlap_dcts.get(dst_lbl, None)
                        if inverse_labeling_exists(rec_dct, dst_lbl, src_lbl):

                            cols.append(1)
                        else:
                            cols.append('')

                    else:  # retrograde
                        # Checking if labeling also present retrograde
                        rec_dct = ant_inj_site_overlap_dcts.get(dst_lbl, None)
                        if inverse_labeling_exists(rec_dct, dst_lbl, src_lbl):

                            cols.append(1)
                        else:
                            cols.append('')

                else:
                    cols.append('')
            csvwriter.writerow(cols)  # string technically a sequence

    pct_str = "\r{0:0.2f}% complete... ".format(100)
    print(pct_str)

    output_pickle_path = cic_utils.pickle_path(output_ctx_mat_csv)
    pickle_dct = cic_utils.pickle_dct(args)
    pickle.dump(pickle_dct, open(output_pickle_path, "wb"))


# Checks if labeling exists for the inverse(?) ant/ret
def inverse_labeling_exists(inverse_dct, dst_lbl, src_lbl):
    if inverse_dct is not None:
        rec_tup = inverse_dct.get(src_lbl, None)
        if rec_tup is not None and len(rec_tup) > 0:
            assert len(rec_tup) == 2, \
                "overlap tup: {}".format(rec_tup)
            source_only = rec_tup[0]
            overlap = rec_tup[1]
            assert source_only + overlap > 0, \
                "WARNING: cell {} has no source or overlap".format(
                    dst_lbl)
            if overlap != 0:
                return True
    return False


def mat_olp_calc(source_only, overlap):
    return float(overlap)/float(source_only + overlap)


# Normalization calculator
def normalize_calc(maximum, minimum, value):
    if maximum - minimum == 0:
        return minimum
    return float(value - minimum)/float(maximum - minimum)


if __name__ == '__main__':
    main()
