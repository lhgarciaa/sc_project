import unittest
from src import cic_outspector


class TestCicOutspector(unittest.TestCase):
    def setUp(self):
        self.case_dir = 'test_data/test_cic_outspector/SW120228-02B/'
        self.ch = '2'
        self.exp_overlap_dir_path = \
            'test_data/test_cic_outspector/SW120228-02B/overlap/2'
        self.lvl = '53'
        self.exp_opairs_section = 'SW120228-02B_2_01'
        self.exp_thresh_dir_path = 'test_data/test_cic_outspector/SW120228-02B/threshold/channels/2'  # noqa: E501
        self.exp_thresh_tif_path = 'test_data/test_cic_outspector/SW120228-02B/threshold/channels/2/SW120228-02B_2_01_ch2-th.tif'  # noqa: E501
        self.gcs = '350'
        self.exp_overlap_path = 'test_data/test_cic_outspector/SW120228-02B/overlap/2/SW120228-02B_2_01_ch2_grid-350.csv'  # noqa: E501
        self.exp_atlas_tif_path = '/ifs/loni/faculty/dong/mcp/atlas_roigb/053_2013_rgb-01_append.tif'  # noqa: E501

    def test_overlap_dir_path(self):
        overlap_dir_path = cic_outspector.overlap_dir_path(
            case_dir=self.case_dir,
            ch=self.ch)

        self.assertEqual(self.exp_overlap_dir_path, overlap_dir_path)

    def test_opairs_section(self):
        opairs_section = cic_outspector.opairs_section(
            case_dir=self.case_dir,
            lvl=self.lvl)
        self.assertEqual(self.exp_opairs_section, opairs_section)

    def test_overlap_path(self):
        overlap_dir_path = cic_outspector.overlap_dir_path(
            case_dir=self.case_dir,
            ch=self.ch)
        opairs_section = cic_outspector.opairs_section(
            case_dir=self.case_dir,
            lvl=self.lvl)
        overlap_path = cic_outspector.overlap_path(
            overlap_dir_path=overlap_dir_path,
            opairs_section=opairs_section,
            ch=self.ch,
            gcs=self.gcs)
        self.assertEqual(self.exp_overlap_path, overlap_path)

    def test_thresh_dir_path(self):
        thresh_dir_path = cic_outspector.thresh_dir_path(
            case_dir=self.case_dir,
            ch=self.ch)

        self.assertEqual(self.exp_thresh_dir_path, thresh_dir_path)

    def test_thresh_tif_path(self):
        opairs_section = cic_outspector.opairs_section(
            case_dir=self.case_dir,
            lvl=self.lvl)
        thresh_dir_path = cic_outspector.thresh_dir_path(
            case_dir=self.case_dir,
            ch=self.ch)
        thresh_tif_path = cic_outspector.thresh_tif_path(
            thresh_dir_path=thresh_dir_path,
            opairs_section=opairs_section,
            ch=self.ch)
        self.assertEqual(self.exp_thresh_tif_path, thresh_tif_path)

    def test_atlas_tif_path(self):
        atlas_tif_path = cic_outspector.atlas_tif_path(lvl=self.lvl)

        self.assertEqual(self.exp_atlas_tif_path, atlas_tif_path)
