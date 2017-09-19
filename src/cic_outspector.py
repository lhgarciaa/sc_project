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
def cmt_clr_thresh(cons_cmt_csv_path, thresh_tif_path, overlap_path, lvl, gcs,
                   hemi):
    cons_cmt_str = cic_plot.cons_cmt_str(
        cons_cmt_csv_path=cons_cmt_csv_path,
        lvl=lvl)
    thesh_tif = cic_plot.thresh_tif(thresh_tif_path=thresh_tif_path)
    (meta_dct, header_lst, rows) = \
        cic_overlap.read_overlap_csv(inpust_csv_path=overlap_path)

    for row in rows:
        # if in hemi
        #  get threshold column and row
        #   get cell_img from column and row
        #    get threshold value at column and row
        #    get overlap at column and row
        #    if theshold xor overlap then error
        #    get cmt index of overlap
        #    use cmt index to color threshold image
        #    return threshold image

        location = jfkdlsj
        row_hemi = fkdjs
        if hemi == row_hemi:
            ccs_fmt_location = fjdklsa
            cmt_idx = -1
            for idx, cmt in enumerate(cons_cmt_str):
                if ccs_fmt_cell in cmt:
                    cmt_idx = idx
            assert cmd_idx != -1, "Nope! {} in {} but not in {}".format(
                location,
                overlap_path,
                char_cmt_csv_path)
            # first get cell image from row, col using grid cell size
            cell_img = cic_plot.cell_img(thresh_tif_path=thresh_tif_path,
                                row=row, col=col, gcs=gcs)

            assert cic_plot.has_thresh(cell_img),\
                "Nope! Location {} and {} show overlap but cell image blank".\
                format(location, ccs_fmt_cell)

            # essentially copy threshold grid cell at row and col to thresh out
            cmt_clr_thresh_out_img = cic_plot.color_thresh(cell_img=cell_img,
                row=row, col=col, gcs=gcs,
                cmt_clr_thresh_out_img=cmt_clr_thresh_out_img)
    return cmt_clr_thresh_out_img
