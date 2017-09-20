import cv2
import os
import csv
import ast
import numpy as np


class BoundingBox:
    '''
    We Use this bounding box extraction regularly so lets extract and abstract
        bool_array is 2d array where region to be bound
        (edges determined) is true and everything else is false
    '''
    @staticmethod
    def get_edges(bool_twodarray):
        xmin = 0
        ymin = 0
        xmax = bool_twodarray.shape[1] - 1
        ymax = bool_twodarray.shape[0] - 1
        # find xmin
        looking = True
        x = xmin
        while looking:
            col = bool_twodarray[:, x]
            if col.any():
                looking = False
                xmin = x
            x += 1
            if x >= xmax:
                xmin = 0
                looking = False
        # find xmax
        looking = True
        x = xmax
        while looking:
            col = bool_twodarray[:, x]
            if col.any():
                looking = False
                xmax = x
            x -= 1
            if x <= 0:
                xmax = bool_twodarray.shape[1] - 1
                looking = False
        # find ymin
        looking = True
        y = ymin
        while looking:
            row = bool_twodarray[y, :]
            if row.any():
                looking = False
                ymin = y
            y += 1
            if y >= ymax:
                ymin = 0
                looking = False
        # find xmax
        looking = True
        y = ymax
        while looking:
            row = bool_twodarray[y, :]
            if row.any():
                looking = False
                ymax = y
            y -= 1
            if y <= 0:
                ymax = bool_twodarray.shape[0] - 1
                looking = False
        return (xmin, xmax, ymin, ymax)


# atlas - rgb atlas file
# t - ndarray with dtype = bool
#     true for any non-white pixel element in rgb atlas file
# returns 4 element tuple (
# xmin - leftmost non-white atlas pixel (region)
# xmax - rightmost non-white atlas pixel (region)
# ymin - topmost non-while atlas pixel (region)
# ymax - bottommost non-white atlas pixel (region)
def get_edges(rgb_code):
    WHITE = 255 * 256 * 256 + 255 * 256 + 255
    t = rgb_code != WHITE
    return BoundingBox.get_edges(t)


#  return sorted list of frozensets corresponding to communities in consensus
#   only of images with threshold level
#   note this method assumes cmt structure is made up of grid cells
def cons_cmt_str(cons_cmt_csv_path, lvl):
    assert os.path.isfile(cons_cmt_csv_path), "No csv {}".format(
        cons_cmt_csv_path)
    cons_cmt_str = None
    with open(cons_cmt_csv_path) as csvfile:
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


# does not change color channels
def atlas_tif(atlas_tif_path):
    assert os.path.isfile(atlas_tif_path), \
        "No tif {}".format(atlas_tif_path)
    return cv2.imread(atlas_tif_path, cv2.IMREAD_UNCHANGED)


#  edges_tup - (xmin, xmax, ymin, ymax)
#  row - row in pixels (not grid cells)
#  col - col in pixels (not grid cells)
#  gcs - grid cell size
def cell_img(grid_thresh_img, y, x, gcs, hemi, edges_tup):
    (xmin, xmax, ymin, ymax) = edges_tup
    midx = grid_thresh_img.shape[1] / 2
    y_stop = min(x + gcs, ymax)
    if hemi == 'l':
        x_stop = min(x + gcs, midx)
    if hemi == 'r':
        x_stop = min(x + gcs, xmax)
    cell_img = grid_thresh_img[y:y_stop, x:x_stop]
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
