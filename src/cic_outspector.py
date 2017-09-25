import os
import cic_overlap
import cic_plot


def overlap_dir_path(case_dir, ch):
    assert os.path.isdir(case_dir)
    overlap_ch_path = os.path.join('overlap', ch)
    return os.path.join(case_dir, overlap_ch_path)


# returns None if no matching section found for atlas lvl
def opairs_section(case_dir, lvl):
    assert os.path.isdir(case_dir)
    opairs_path = os.path.join(case_dir, 'opairs.lst')
    with open(opairs_path) as opairs_lst:
        rows = opairs_lst.readlines()
    for row in rows:
        cols = row.split()
        if len(cols) > 0:
            if int(cols[1]) == int(lvl):
                return cols[0]
    return None


def overlap_path(overlap_dir_path, opairs_section, ch, gcs):
    base_csv = opairs_section + '_ch' + ch + '_grid-' + gcs + '.csv'
    return os.path.join(overlap_dir_path, base_csv)


def thresh_dir_path(case_dir, ch):
    assert os.path.isdir(case_dir)
    return os.path.join(case_dir, 'threshold/channels/' + ch)


def thresh_tif_path(thresh_dir_path, opairs_section, ch):
    base_tif = opairs_section + '_ch' + ch + '-th.tif'
    return os.path.join(thresh_dir_path, base_tif)


#  return threshold tif image from path
def thresh_tif(thresh_tif_path):
    return None


def atlas_tif_path(lvl):
    pref_str = "{:03}".format(int(lvl))
    base_name = pref_str + '_2013_rgb-01_append.tif'
    return os.path.join('/ifs/loni/faculty/dong/mcp/atlas_roigb', base_name)


# colorize thresh_tif_path image by index of cmt in cons_cmt_csv_path
def cmt_clr_thresh(cons_cmt_csv_path, thresh_tif_path, overlap_path,
                   atlas_tif_path, gcs, lvl, hemi):
    assert type(gcs) == int
    assert type(lvl) == int
    assert type(hemi) == str
    cons_cmt_str = cic_plot.cons_cmt_str(
        cons_cmt_csv_path=cons_cmt_csv_path,
        lvl=lvl)
    thresh_img = cic_plot.thresh_tif(thresh_tif_path=thresh_tif_path)
    overlap_tup = \
        cic_overlap.read_overlap_csv(input_csv_path=overlap_path)
    (meta_dct, header_lst, overlap_rows) = overlap_tup
    dct_gcs = int(meta_dct['Grid Size'])
    dct_lvl = int(meta_dct['ARA Level'])

    assert gcs == dct_gcs and lvl == dct_lvl, \
        "{} gcs != {} dct_gcs and {} != {} dct_lvl".format(gcs, dct_gcs,
                                                           lvl, dct_lvl)

    atlas_img = cic_plot.atlas_tif(atlas_tif_path)
    edges_tup = cic_plot.get_edges(atlas_img)
    (xmin, xmax, ymin, ymax) = edges_tup

    assert hemi == 'r', "cic_outspector only handles hemi = 'r' but hemi = \
    '{}'".format(hemi)
    grid_thresh_img = thresh_img[ymin:ymax, xmin:xmax]
    midx = thresh_img.shape[1] / 2
    if hemi == 'r':
        x = midx
        y = 0

        while x < xmax:
            while y < ymax:
                # get cell_img from y, x plus gcs
                cell_img = cic_plot.cell_img(grid_thresh_img=grid_thresh_img,
                                             y=y, x=x, gcs=gcs, hemi=hemi,
                                             edges_tup=edges_tup)

                if cic_plot.has_thresh(cell_img):
                    # get overlap at x/gcs column and y/gcs row
                    overlap_row = cic_overlap.overlap_row(overlap_tup,
                                                          hemi=hemi,
                                                          col=x/gcs,
                                                          row=y/gcs)
                    # if theshold labelling but no overlap then error
                    assert overlap_row is not None, \
                        "Threshold at {} in {} but no overlap value in {}".\
                        format((hemi, x/gcs, y/gcs),
                               thresh_tif_path,
                               overlap_path)

                    # get cmt index of overlap
                    cmt_idx = cic_plot.cmt_idx(cons_cmt_str,
                                               lvl=lvl,
                                               hemi=hemi,
                                               col=x/gcs,
                                               row=y/gcs)
                    # if overlap value not in any community then error
                    assert cmt_idx is not None, "Found cmt {} but "
                    "{} not in {}".format((hemi, x/gcs, y/gcs),
                                          (lvl, hemi, x/gcs, y/gcs),
                                          cons_cmt_csv_path)

                    # color cell image by community
                    cmt_clr_cell_img = cic_plot.clr_thresh(cell_img=cell_img,
                                                           clr_idx=cmt_idx)
                    # paste cell image into grid_thresh_img
                    cic_plot.paste_cell_img(cell_img=cmt_clr_cell_img,
                                            y=y, x=x, gcs=gcs,
                                            grid_thresh_img=grid_thresh_img)

        # finally, paste grid thresh_img into thresh_img and return
        thresh_img[ymin:ymax, xmin:xmax] = grid_thresh_img
        return thresh_img
