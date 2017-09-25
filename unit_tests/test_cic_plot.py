import unittest
from src import cic_plot
import os
import numpy as np
import cv2


class TestCicPlot(unittest.TestCase):
    def setUp(self):
        self.lvl = 53
        self.hemi = 'r'
        self.gcs = 350
        self.thresh_tif_path = 'test_data/test_cic_plot/small_thresh.tif'
        self.cmt_clr_thresh_tif_path = \
            'test_data/test_cic_plot/cell_thresh_right_red.tif'
        self.cons_cmt_str_csv_path = 'test_data/test_cic_plot/cons_cmt_str.csv'
        self.pasted_thresh_tif_path = \
            'test_data/test_cic_plot/pasted_thresh.tif'
        self.exp_cons_cmt_str = \
            [frozenset(['(53:r:16:10)', '(53:r:16:11)']), frozenset([]),
             frozenset([])]
        self.exp_cmt_idx = 0
        img = cic_plot.thresh_tif(thresh_tif_path=self.thresh_tif_path)
        self.edges_tup = (0, 700, 0, 350)
        (xmin, xmax, ymin, ymax) = self.edges_tup
        self.grid_thresh_img = img[ymin:ymax, xmin:xmax]

    def test_cell_img(self):
        cell_img = cic_plot.cell_img(grid_thresh_img=self.grid_thresh_img,
                                     y=0, x=0, gcs=self.gcs, hemi='r',
                                     edges_tup=self.edges_tup)
        self.assertIsNotNone(cell_img)
        height_width_tup = cell_img.shape[:2]
        self.assertEqual((self.gcs, self.gcs), height_width_tup)

    def test_cons_cmt_str(self):
        cons_cmt_str = cic_plot.cons_cmt_str(self.cons_cmt_str_csv_path,
                                             self.lvl)
        self.assertEqual(self.exp_cons_cmt_str, cons_cmt_str)

    def test_cmt_idx(self):
        cons_cmt_str = cic_plot.cons_cmt_str(self.cons_cmt_str_csv_path,
                                             self.lvl)
        cmt_idx = cic_plot.cmt_idx(cons_cmt_str=cons_cmt_str,
                                   lvl=self.lvl,
                                   hemi=self.hemi,
                                   col=16,
                                   row=11)
        self.assertEqual(self.exp_cmt_idx, cmt_idx)
        cmt_idx = cic_plot.cmt_idx(cons_cmt_str=cons_cmt_str,
                                   lvl=self.lvl,
                                   hemi=self.hemi,
                                   col=16,
                                   row=4393909)
        self.assertIsNone(cmt_idx)

    def test_paste_cell_img(self):
        # create clr_thresh from cell_img
        cell_img = cic_plot.cell_img(grid_thresh_img=self.grid_thresh_img,
                                     y=0,
                                     x=self.gcs,
                                     gcs=self.gcs,
                                     hemi='r',
                                     edges_tup=self.edges_tup)
        clr_idx = 0  # pretend like this cell corresponds to (53:r:16:10)
        clr_thresh = cic_plot.clr_thresh(cell_img=cell_img,
                                         clr_idx=clr_idx)

        # now paste clr_thresh into thresh_img
        thresh_img = cic_plot.gray2bgra_tif(self.thresh_tif_path)
        cic_plot.paste_cell_img(cell_img=clr_thresh,
                                y=0,
                                x=self.gcs,
                                gcs=self.gcs,
                                hemi='r',
                                edges_tup=self.edges_tup,
                                idx=0,
                                grid_thresh_img=thresh_img)

        # check that pasted clr_thresh appears in thresh_img as expected
        exp_pasted_thresh = cv2.imread(self.pasted_thresh_tif_path,
                                       cv2.IMREAD_UNCHANGED)
        self.assertEqual(exp_pasted_thresh.shape, thresh_img.shape)
        self.assertFalse(np.bitwise_xor(exp_pasted_thresh, thresh_img).any())

    def test_thresh_tif(self):
        thresh_tif = cic_plot.thresh_tif(self.thresh_tif_path)
        self.assertIsNotNone(thresh_tif)

    def test_has_thresh(self):
        self.assertTrue(os.path.isfile(self.thresh_tif_path))
        cell_img = cic_plot.cell_img(grid_thresh_img=self.grid_thresh_img,
                                     y=0, x=0, gcs=self.gcs, hemi='r',
                                     edges_tup=self.edges_tup)
        self.assertFalse(cic_plot.has_thresh(cell_img))
        cell_img = cic_plot.cell_img(grid_thresh_img=self.grid_thresh_img,
                                     y=0,
                                     x=self.gcs,
                                     gcs=self.gcs, hemi='r',
                                     edges_tup=self.edges_tup)
        self.assertTrue(cic_plot.has_thresh(cell_img))

    def test_clr_thresh(self):
        cell_img = cic_plot.cell_img(grid_thresh_img=self.grid_thresh_img,
                                     y=0,
                                     x=self.gcs,
                                     gcs=self.gcs, hemi='r',
                                     edges_tup=self.edges_tup)
        assert os.path.isfile(self.cmt_clr_thresh_tif_path), \
            "No tif {}".format(self.cmt_clr_thresh_tif_path)
        exp_clr_thresh = cv2.imread(self.cmt_clr_thresh_tif_path,
                                    cv2.IMREAD_UNCHANGED)
        clr_idx = 0  # pretend like this cell corresponds to (53:r:16:10)
        clr_thresh = cic_plot.clr_thresh(cell_img=cell_img,
                                         clr_idx=clr_idx)
        self.assertEqual(exp_clr_thresh.shape, clr_thresh.shape)
        self.assertFalse(np.bitwise_xor(exp_clr_thresh, clr_thresh).any())
