import unittest
from src import cic_utils
import os


class TestHPfUtils(unittest.TestCase):
    def setUp(self):
        self.TEST_DATA_DIR = 'test_data'

    def test_pckl_path(self):
        in_path = 'some_dir/some_subdir/somepath.csv'
        exp_pickle_path = 'some_dir/some_subdir/.somepath.p'
        pickle_path = cic_utils.pickle_path(in_path)

        self.assertEqual(exp_pickle_path, pickle_path)

    # TEST READING RECT MATRIX
    def test_read_ctx_mat(self):
        # simple_rect_mat.csv:
        #  ,C
        #  A,1
        #  B,
        exp_col_roi_lst = ['C']
        exp_row_roi_lst = ['A', 'B']

        input_csv_path = os.path.join(
            self.TEST_DATA_DIR, 'simple_rect_mat.csv')
        (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) =\
            cic_utils.read_ctx_mat(input_csv_path)

        self.assertEqual(exp_col_roi_lst, col_roi_name_npa.tolist())
        self.assertEqual(len(exp_col_roi_lst), ctx_mat_npa.shape[1])

        self.assertEqual(exp_row_roi_lst, row_roi_name_npa.tolist())
        self.assertEqual(len(exp_row_roi_lst), ctx_mat_npa.shape[0])

        self.assertEqual(1, ctx_mat_npa[0][0])

        self.assertFalse(
            cic_utils.is_sq(
                row_roi_name_npa, col_roi_name_npa, ctx_mat_npa))

    # TEST CONVERTING RECT MATRIX TO PADDED SQUARE
    def test_pad_rect_ctx_mat_to_sq(self):
        csv_paths = ['simple_rect_mat.csv', 'complex_rect_mat.csv']
        exp_sq_roi_lst_dct = {csv_paths[0]: (['A', 'B'], ['C', 'NONE_00001']),
                              csv_paths[1]: (['A', 'B', 'X'], ['C', 'D', 'X'])}

        for base_path in csv_paths:
            # first read matrix and make sure it's not square
            input_csv_path = os.path.join(
                self.TEST_DATA_DIR, base_path)
            (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) =\
                cic_utils.read_ctx_mat(input_csv_path)
            self.assertFalse(
                cic_utils.is_sq(row_roi_name_npa,
                                col_roi_name_npa,
                                ctx_mat_npa))

            # now convert and make sure square and values set correctly
            (pad_row_roi_name_npa,
             pad_col_roi_name_npa,
             sq_ctx_mat_npa) = cic_utils.pad_rect_ctx_mat_to_sq(
                    row_roi_name_npa, col_roi_name_npa, ctx_mat_npa)

            # should be for simple:
            #    C NONE_00001
            #  A 1
            #  B

            # or should be for complex:
            #    C D X
            #  A 1
            #  B
            #  X

            exp_sq_roi_lst_tup = exp_sq_roi_lst_dct[base_path]

            self.assertEqual(
                exp_sq_roi_lst_tup[0], pad_row_roi_name_npa.tolist())
            self.assertEqual(
                exp_sq_roi_lst_tup[1], pad_col_roi_name_npa.tolist())
            self.assertEqual(
                len(exp_sq_roi_lst_tup[1]), sq_ctx_mat_npa.shape[0])
            self.assertEqual(
                len(exp_sq_roi_lst_tup[1]), sq_ctx_mat_npa.shape[1])

            # will return false because row vs. col rois are different
            self.assertFalse(
                cic_utils.is_sq(pad_row_roi_name_npa,
                                pad_col_roi_name_npa,
                                sq_ctx_mat_npa))

            self.assertEqual(1, sq_ctx_mat_npa[0][0])

    # TEST CONVERTING RECT MATRIX TO SQUARE
    def test_conv_rect_ctx_mat_to_sq(self):
        # test simple and complex rect
        #  complex_rect_mat.csv, note same num rois in rows/cols
        #  ,C,D,X
        #  A,1,,
        #  B,,,
        #  X,,,

        csv_paths = ['simple_rect_mat.csv', 'complex_rect_mat.csv']
        exp_sq_roi_lst_dct = {csv_paths[0]: ['A', 'B', 'C'],
                              csv_paths[1]: ['A', 'B', 'C', 'D', 'X']}

        for base_path in csv_paths:
            print "testing convert to square {}...".format(base_path)

            # first read matrix and make sure it's not square
            input_csv_path = os.path.join(
                self.TEST_DATA_DIR, base_path)
            (row_roi_name_npa, col_roi_name_npa, ctx_mat_npa) =\
                cic_utils.read_ctx_mat(input_csv_path)
            self.assertFalse(cic_utils.is_sq(row_roi_name_npa,
                                             col_roi_name_npa,
                                             ctx_mat_npa))

            # now convert and make sure square and values set correctly
            (sq_roi_name_npa, sq_ctx_mat_npa) =\
                cic_utils.conv_rect_ctx_mat_to_sq(
                row_roi_name_npa, col_roi_name_npa, ctx_mat_npa)

            # should be for simple
            #    A B C
            #  A     1
            #  B
            #  C

            # or should be for complex
            #   A B C D X
            # A     1
            # B
            # C
            # D
            # X

            exp_sq_roi_lst = exp_sq_roi_lst_dct[base_path]

            self.assertEqual(exp_sq_roi_lst, sq_roi_name_npa.tolist())
            self.assertEqual(len(exp_sq_roi_lst), sq_ctx_mat_npa.shape[0])
            self.assertEqual(len(exp_sq_roi_lst), sq_ctx_mat_npa.shape[1])

            self.assertTrue(
                cic_utils.is_sq(sq_roi_name_npa,
                                sq_roi_name_npa,
                                sq_ctx_mat_npa))

            self.assertEqual(1, sq_ctx_mat_npa[0][2])
