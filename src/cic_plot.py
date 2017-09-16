import cv2
import os
import csv
import ast
import numpy as np


#  return sorted list of frozensets corresponding to communities in consensus
#   only of images with threshold level
#   note this method assumes cmt structure is made up of grid cells
def cons_cmt_str(cons_cmt_str_csv_path, lvl):
    assert os.path.isfile(cons_cmt_str_csv_path), "No csv {}".format(
        cons_cmt_str_csv_path)
    cons_cmt_str = None
    with open(cons_cmt_str_csv_path) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if 'consensus com str' in row[0]:
                cons_cmt_str_lst_lst = ast.literal_eval(row[1])
                cons_cmt_str = []
                for lst in cons_cmt_str_lst_lst:
                    lvl_lst = []
                    for cell in lst:
                        if cell.startswith('({}:'.format(lvl)):
                            lvl_lst.append(cell)
                    cons_cmt_str.append(frozenset(lvl_lst))
    return cons_cmt_str


# assumes and returns grayscale
def thresh_tif(thresh_tif_path):
    assert os.path.isfile(thresh_tif_path), \
        "No tif {}".format(thresh_tif_path)
    return cv2.imread(thresh_tif_path, cv2.IMREAD_GRAYSCALE)


def cell_img(thresh_tif_path, row, col, gcs):
    row_stop = row + gcs
    col_stop = col + gcs
    img = thresh_tif(thresh_tif_path=thresh_tif_path)
    cell_img = img[row:row_stop, col:col_stop]
    return cell_img


def has_thresh(cell_img):
    # do bitwise_not since are actually testing for black since thresh
    #  represented as black... bitwise_not converts black to white, then
    #  we test for white
    # any() checks if anything evaluates to True i.e. not zero
    return (cv2.bitwise_not(cell_img).any())

# assume cell_img is one channel
def color_thresh(cell_img, clr_idx):
    assert len(cell_img.shape) <= 2, \
        "cell_img {} channels, expected 2".format(cell_img.shape[2])
    clr_arr = [[0,   0,   255, 255],
               [0,   255,   0, 255],
               [255,    0,  0, 255]]
    # got this technique from
    #  https://stackoverflow.com/questions/14786179/
    #  how-to-convert-a-1-channel-image-into-a-3-channel-with-opencv2
    new_img = cv2.cvtColor(cell_img, cv2.COLOR_GRAY2BGRA)

    new_img[np.where((new_img == [0, 0, 0, 255]).all(axis=2))] = \
        clr_arr[clr_idx]
    return new_img
