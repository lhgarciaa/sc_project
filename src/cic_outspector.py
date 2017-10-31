import os
import cic_overlap
import cic_plot
import numpy as np
import cv2


def overlap_dir_path(case_dir, ch):
    assert os.path.isdir(case_dir)
    overlap_ch_path = os.path.join('overlap', ch)
    return os.path.join(case_dir, overlap_ch_path)


# returns None if no matching section found for atlas lvl
def opairs_section(case_dir, lvl):
    assert os.path.isdir(case_dir)
    opairs_path = os.path.join(case_dir, 'opairs.lst')
    with open(opairs_path, 'r') as opairs_lst:
        rows = opairs_lst.readlines()
    for row in rows:
        cols = row.split()
        if len(cols) > 0:
            if int(cols[1]) == int(lvl):
                return cols[0]
    return None


def grid_ref_tif_path(overlap_path, ch):
    return overlap_path.\
        replace("_ch{}".format(ch), "").\
        replace("_cellcount", "").\
        replace(".csv", "_ref.tif")


def overlap_path(overlap_dir_path, opairs_section, ch, gcs):
    base_csv = opairs_section + '_ch' + ch + '_grid-' + gcs + '.csv'
    return os.path.join(overlap_dir_path, base_csv)


def cellcount_or_overlap_path(overlap_dir_path, opairs_section, ch, gcs):
    base_csv = opairs_section + '_ch' + ch + '_grid-' + gcs + '.csv'
    or_overlap_path = os.path.join(overlap_dir_path, base_csv)

    cellcount_base = \
        opairs_section + '_ch' + ch + '_grid-' + gcs + '_cellcount.csv'
    cellcount = os.path.join(overlap_dir_path, cellcount_base)
    if os.path.isfile(cellcount):
        return cellcount
    else:
        assert(os.path.isfile(or_overlap_path))
        return or_overlap_path


def thresh_dir_path(case_dir, ch):
    assert os.path.isdir(case_dir)
    return os.path.join(case_dir, 'threshold/channels/' + ch)


def thresh_tif_path(thresh_dir_path, opairs_section, ch):
    base_tif = opairs_section + '_ch' + ch + '-th.tif'
    return os.path.join(thresh_dir_path, base_tif)


def degenerate_or_thresh_tif_path(thresh_dir_path, opairs_section, ch):
    base_tif = opairs_section + '_ch' + ch + '-th.tif'
    or_thresh_tif_path = os.path.join(thresh_dir_path, base_tif)

    degenerate_base = opairs_section + '_ch' + ch + '-degenerate.tif'
    degenerate = os.path.join(thresh_dir_path, degenerate_base)

    if os.path.isfile(degenerate):
        return degenerate
    else:
        assert os.path.isfile(or_thresh_tif_path)
        return or_thresh_tif_path


# check for degenrate here, too
def roi_filter_or_thresh_tif_path(thresh_dir_path, opairs_section, ch):
    or_thresh_tif_path = degenerate_or_thresh_tif_path(
        thresh_dir_path=thresh_dir_path,
        opairs_section=opairs_section,
        ch=ch)
    roi_filter = output_roi_filter_tif_path(thresh_dir_path=thresh_dir_path,
                                            thresh_tif_path=or_thresh_tif_path)
    if os.path.isfile(roi_filter):
        return roi_filter
    else:
        assert(os.path.isfile(or_thresh_tif_path))
        return or_thresh_tif_path


def output_roi_filter_overlap_csv_path(overlap_dir_path, overlap_path):
    new_base = os.path.splitext(os.path.basename(overlap_path))[0] + \
               "_roi_filter" + \
               os.path.splitext(os.path.basename(overlap_path))[1]
    return os.path.join(overlap_dir_path, new_base)


# simply appends "_visual" to end of base name before extension
def visual_path(thresh_dir_path, thresh_tif_path):
    new_base = os.path.splitext(os.path.basename(thresh_tif_path))[0] + \
               "_visual" + \
               os.path.splitext(os.path.basename(thresh_tif_path))[1]
    return os.path.join(thresh_dir_path, new_base)


def output_roi_filter_tif_path(thresh_dir_path, thresh_tif_path):
    new_base = os.path.splitext(os.path.basename(thresh_tif_path))[0] + \
               "_roi_filter" + \
               os.path.splitext(os.path.basename(thresh_tif_path))[1]
    return os.path.join(thresh_dir_path, new_base)


def cmt_clr_tif_path(thresh_dir_path, thresh_tif_path):
    new_base = os.path.splitext(os.path.basename(thresh_tif_path))[0] + \
               "_cmt_clr" + \
               os.path.splitext(os.path.basename(thresh_tif_path))[1]
    return os.path.join(thresh_dir_path, new_base)


def agg_cmt_clr_tif_path(cmt_clr_tif_path, output_dir_path, lvl):
    end = "_agg_cmt_clr.tif"
    if "degenerate" in cmt_clr_tif_path:
        end = "_agg_degenerate_cmt_clr.tif"

    assert os.path.isdir(output_dir_path)
    pref_str = "{:03}".format(int(lvl))
    base_name = pref_str + end
    return os.path.join(output_dir_path, base_name)


def atlas_tif_path(lvl):
    pref_str = "{:03}".format(int(lvl))
    base_name = pref_str + '_2013_rgb-01_append.tif'
    return os.path.join('/ifs/loni/faculty/dong/mcp/atlas_roigb', base_name)


# an execution_method
def check_and_paste(**args):
    exp_arg_lst = ['header_lst', 'overlap_row', 'incl_lst', 'excl_lst',
                   'cell_img', 'y', 'x', 'gcs', 'hemi', 'gt_edges_tup',
                   'new_grid_thr_img', 'pasted_overlap_rows']

    assert set(exp_arg_lst).issubset(args.keys()), \
        "Uh-oh, did not find {} in {}".format(
            list(set(exp_arg_lst).difference(args.keys())), args.keys())

    # now paste cell into grid thresh img or not
    #  depending on roi list
    if cic_overlap.should_incl_not_excl(
            header_lst=args['header_lst'],
            overlap_row=args['overlap_row'],
            incl_lst=args['incl_lst'],
            excl_lst=args['excl_lst']):
        cic_plot.paste_cell_img(
            cell_img=args['cell_img'],
            y=args['y'],
            x=args['x'],
            gcs=args['gcs'],
            hemi=args['hemi'],
            edges_tup=args['gt_edges_tup'],
            grid_thresh_img=args['new_grid_thr_img'])

        # paste overlap or not depending on roi list
        args['pasted_overlap_rows'].append(args['overlap_row'])


# calls march_through_overlp_thresh with check_and_paste execution method
def roi_filter_thresh_ovlp(roi_filter_csv_path, thresh_tif_path, overlap_path,
                           atlas_tif_path, gcs, lvl, hemi, opairs_section,
                           verbose):
    roi_filter_tup = \
        cic_overlap.read_overlap_csv(input_csv_path=roi_filter_csv_path)
    (incl_lst, excl_lst) = cic_overlap.incl_excl_tup(
        roi_filter_csv_tup=roi_filter_tup,
        opairs_section=opairs_section)

    if verbose:
        print("ROI filtering {}\nusing roi filter csv {}".format(
            opairs_section,
            roi_filter_csv_path))
        print("include list {}\nexclude list {}".format(incl_lst, excl_lst))

    thresh_img = cic_plot.thresh_tif(thresh_tif_path=thresh_tif_path)
    return march_through_ovlp_thresh(
        incl_lst=incl_lst,
        excl_lst=excl_lst,
        thresh_img=thresh_img,
        overlap_path=overlap_path,
        atlas_tif_path=atlas_tif_path,
        gcs=gcs,
        lvl=lvl,
        hemi=hemi,
        opairs_section=opairs_section,
        execution_method=check_and_paste,
        verbose=verbose)


# calls march_through_ovlp_thresh with cmt_clr_thresh_cell execution_method
#  colorize thresh_tif_path image by index of cmt in cons_cmt_csv_path
def cmt_clr_thresh(cons_cmt_csv_path, thresh_tif_path, overlap_path,
                   atlas_tif_path, gcs, lvl, hemi, verbose):
    if verbose:
        print("CMT coloring {}".format(thresh_tif_path))

    cons_cmt_str = cic_plot.cons_cmt_str(
        cons_cmt_csv_path=cons_cmt_csv_path,
        lvl=lvl)

    thresh_img = cic_plot.gray2bgra_tif(tif_path=thresh_tif_path)
    tup = march_through_ovlp_thresh(
        cons_cmt_str=cons_cmt_str,
        thresh_img=thresh_img,
        overlap_path=overlap_path,
        atlas_tif_path=atlas_tif_path,
        gcs=gcs,
        lvl=lvl,
        hemi=hemi,
        execution_method=cmt_clr_thresh_cell,
        verbose=verbose)
    return tup[1]  # return just the thresh_img


# calls march_through_ovlp_thresh with agg_cmt_clr_thresh_cell execution_method
#  simply aggregate cmt_clr_tif_path with agg_cmt_clr_tif_path
def agg_cmt_clr_thresh(cmt_clr_tif_path, agg_cmt_clr_tif_path,
                       gcs, lvl, hemi, verbose):

    if verbose:
        print("Aggregating cmt coloring {} with {}".format(
            cmt_clr_tif_path, agg_cmt_clr_tif_path))

    # use the community colored threshhold image as "thresh_img"
    assert os.path.isfile(cmt_clr_tif_path), \
        "No cmt color tif {} found".format(cmt_clr_tif_path)
    thresh_img = cv2.imread(cmt_clr_tif_path, cv2.IMREAD_UNCHANGED)

    # if agg output file exists, open it, otherwise simply copy thresh_img
    if os.path.isfile(agg_cmt_clr_tif_path):
        agg_cmt_clr_tif = cv2.imread(agg_cmt_clr_tif_path,
                                     cv2.IMREAD_UNCHANGED)
    else:
        agg_cmt_clr_tif = thresh_img.copy()

    # ditch the alpha channel for composition
    agg_cmt_clr_tif_bgr = agg_cmt_clr_tif[:, :, :3]

    # do the freakin aggregation  or uh... composition right tf here
    comp_cmt_clr_tif = cic_plot.compose(thresh_img=thresh_img,
                                        ref_img=agg_cmt_clr_tif_bgr,
                                        verbose=verbose)

    return comp_cmt_clr_tif


# an execution_method
def cmt_clr_thresh_cell(**args):
    exp_arg_lst = ['cons_cmt_str', 'cell_img', 'y', 'x', 'gcs', 'lvl', 'hemi',
                   'gt_edges_tup', 'new_grid_thr_img', 'pasted_overlap_rows']
    assert set(exp_arg_lst).issubset(args.keys()), \
        "Uh-oh, did not find {} in {}".format(
            list(set(exp_arg_lst).difference(args.keys())), args.keys())

    # get cmt index of overlap
    cmt_idx = cic_plot.cmt_idx(cons_cmt_str=args['cons_cmt_str'],
                               lvl=args['lvl'],
                               hemi=args['hemi'],
                               col=args['x']/args['gcs'],
                               row=args['y']/args['gcs'])
    # if overlap value not in any community then error
    assert cmt_idx is not None, \
        "Found cmt {} in lvl {} but {} not in {}".format(
            (args['hemi'],
             args['x']/args['gcs'],
             args['y']/args['gcs']),
            args['lvl'],
            (args['lvl'], args['hemi'],
             args['x']/args['gcs'], args['y']/args['gcs']),
            'cons_cmt_csv_path')

    # color cell image by community
    cmt_clr_cell_img = cic_plot.clr_thresh(cell_img=args['cell_img'],
                                           clr_idx=cmt_idx)
    # paste cell image into grid_thresh_img
    cic_plot.paste_cell_img(
        cell_img=cmt_clr_cell_img,
        y=args['y'],
        x=args['x'],
        gcs=args['gcs'],
        hemi=args['hemi'],
        edges_tup=args['gt_edges_tup'],
        grid_thresh_img=args['new_grid_thr_img'])


# returns tup: (overlap_tup, thresh_img)
def march_through_ovlp_thresh(cons_cmt_str=None,
                              incl_lst=None, excl_lst=None, thresh_img=None,
                              agg_cmt_clr_tif=None,
                              overlap_path=None, atlas_tif_path=None,
                              gcs=None, lvl=None, hemi=None,
                              opairs_section=None,
                              execution_method=None, verbose=None):
    assert type(gcs) == int
    assert type(lvl) == int
    assert type(hemi) == str

    overlap_tup = cic_overlap.read_overlap_csv(input_csv_path=overlap_path)
    (meta_dct, header_lst, overlap_rows) = overlap_tup

    dct_gcs = int(meta_dct['Grid Size'])
    dct_lvl = int(meta_dct['ARA Level'])

    assert gcs == dct_gcs and lvl == dct_lvl, \
        "{} gcs != {} dct_gcs and {} != {} dct_lvl".format(gcs, dct_gcs,
                                                           lvl, dct_lvl)

    if verbose:
        print("getting atlas image {}".format(atlas_tif_path))
    atlas_img = cic_plot.atlas_tif(atlas_tif_path)
    if verbose:
        print("getting edges_tup")
    edges_tup = cic_plot.get_edges(atlas_img)
    (xmin, xmax, ymin, ymax) = edges_tup

    assert hemi == 'r', "cic_outspector only handles hemi = 'r' but hemi = \
    '{}'".format(hemi)
    grid_thr_img = thresh_img[ymin:ymax, xmin:xmax]
    # get dimensions and clear canvas to white for image to paste to
    new_grid_thr_img = np.zeros(grid_thr_img.shape)
    new_grid_thr_img[:] = 255
    midx = grid_thr_img.shape[1] / 2
    gt_xmin = gt_ymin = 0
    gt_xmax = grid_thr_img.shape[1]
    gt_ymax = grid_thr_img.shape[0]
    gt_edges_tup = (gt_xmin, gt_xmax, gt_ymin, gt_ymax)
    if verbose:
        print "(xmin, xmax, ymin, ymax) {}".format(edges_tup)
        print "(gt_xmin, gt_xmax, gt_ymin, gt_ymax) {}".format(gt_edges_tup)
        print "midx {}".format(midx)

    # else some other type of cell based marching
    if hemi == 'r':
        pasted_overlap_rows = []
        offset_x = (midx / gcs + 1) * gcs + 1
        x = midx

        while x < gt_xmax:
            y = 0
            if verbose:
                print("calling {} on col {}".format(
                    execution_method.func_name, x/gcs))
            while y < gt_ymax:
                # get cell_img from y, x plus gcs
                cell_img = cic_plot.cell_img(grid_thresh_img=grid_thr_img,
                                             y=y, x=x, gcs=gcs, hemi=hemi,
                                             edges_tup=gt_edges_tup)

                if cic_plot.has_thresh(cell_img):
                    # get overlap at x/gcs column and y/gcs row
                    overlap_row = cic_overlap.overlap_row(
                        overlap_tup=overlap_tup,
                        hemi=hemi,
                        col=x/gcs,
                        row=y/gcs)
                    # if theshold labelling but no overlap then error
                    assert overlap_row is not None, \
                        "Threshold at {} in {} but no overlap value in {}".\
                        format((hemi, x/gcs, y/gcs),
                               thresh_tif_path,
                               overlap_path)

                    execution_method(
                        cons_cmt_str=cons_cmt_str,
                        header_lst=header_lst,
                        overlap_row=overlap_row,
                        incl_lst=incl_lst,
                        excl_lst=excl_lst,
                        cell_img=cell_img,
                        y=y,
                        x=x,
                        gcs=gcs,
                        lvl=lvl,
                        hemi=hemi,
                        gt_edges_tup=gt_edges_tup,
                        new_grid_thr_img=new_grid_thr_img,
                        pasted_overlap_rows=pasted_overlap_rows)

                y += gcs

            if midx % gcs > 0 and x < offset_x:
                x = offset_x
            else:
                x += gcs

        # finally, paste grid thresh_img into thresh_img and return
        thresh_img[ymin:ymax, xmin:xmax] = new_grid_thr_img
        return ((meta_dct, header_lst, pasted_overlap_rows), thresh_img)
