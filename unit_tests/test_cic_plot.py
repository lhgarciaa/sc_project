import unittest
from src import cic_plot
import os
import numpy as np
import cv2


class TestCicPlot(unittest.TestCase):
    def setUp(self):
        self.lvl = 53
        self.gcs = 350
        self.thresh_tif_path = 'test_data/test_cic_plot/small_thresh.tif'
        self.cmt_clr_thresh_tif_path = \
            'test_data/test_cic_plot/cell_thresh_right_red.tif'
        self.cons_cmt_str_csv_path = 'test_data/test_cic_plot/cons_cmt_str.csv'
        self.exp_cons_cmt_str = \
            [frozenset(['(53:r:16:10)', '(53:r:16:11)']), frozenset([]),
             frozenset([])]

    def test_cell_img(self):
        cell_img = cic_plot.cell_img(thresh_tif_path=self.thresh_tif_path,
                                     row=0, col=0, gcs=self.gcs, hemi='r',
                                     edges_tup=(0, 700, 0, 350))
        self.assertIsNotNone(cell_img)
        height_width_tup = cell_img.shape[:2]
        self.assertEqual((self.gcs, self.gcs), height_width_tup)

    def test_cons_cmt_str(self):
        cons_cmt_str = cic_plot.cons_cmt_str(self.cons_cmt_str_csv_path,
                                             self.lvl)
        self.assertEqual(self.exp_cons_cmt_str, cons_cmt_str)

    def test_thresh_tif(self):
        thresh_tif = cic_plot.thresh_tif(self.thresh_tif_path)
        self.assertIsNotNone(thresh_tif)

    def test_has_thresh(self):
        self.assertTrue(os.path.isfile(self.thresh_tif_path))
        cell_img = cic_plot.cell_img(thresh_tif_path=self.thresh_tif_path,
                                     row=0, col=0, gcs=self.gcs, hemi='r',
                                     edges_tup=(0, 700, 0, 350))
        self.assertFalse(cic_plot.has_thresh(cell_img))
        cell_img = cic_plot.cell_img(thresh_tif_path=self.thresh_tif_path,
                                     row=0,
                                     col=self.gcs,
                                     gcs=self.gcs, hemi='r',
                                     edges_tup=(0, 700, 0, 350))
        self.assertTrue(cic_plot.has_thresh(cell_img))

    def test_color_thresh(self):
        cell_img = cic_plot.cell_img(thresh_tif_path=self.thresh_tif_path,
                                     row=0,
                                     col=self.gcs,
                                     gcs=self.gcs, hemi='r',
                                     edges_tup=(0, 700, 0, 350))
        assert os.path.isfile(self.cmt_clr_thresh_tif_path), \
            "No tif {}".format(self.cmt_clr_thresh_tif_path)
        exp_color_thresh = cv2.imread(self.cmt_clr_thresh_tif_path,
                                      cv2.IMREAD_UNCHANGED)
        clr_idx = 0  # pretend like this cell corresponds to (53:r:16:10)
        color_thresh = cic_plot.color_thresh(cell_img=cell_img,
                                             clr_idx=clr_idx)
        self.assertEqual(exp_color_thresh.shape, color_thresh.shape)
        self.assertFalse(np.bitwise_xor(exp_color_thresh, color_thresh).any())
