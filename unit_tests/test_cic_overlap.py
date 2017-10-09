import unittest
from src import cic_overlap
import os


class TestCicOverlap(unittest.TestCase):
    def setUp(self):
        self.test_overlap_csv_path = 'test_data/test_overlap_csv.csv'
        self.test_write_overlap_csv_path = 'test_data/test_write_overlap.csv'
        self.roi_filter_csv = 'test_data/roi_filter_thresh_ovlp/SW120228-02B/SW120228-02B_roi_filter_ch2_grid-350.csv'  # noqa
        """
        Metalines: 10
        Project Name: SW010101-01A
        Case Name: SW010101-01A
        Slide Number: 1_09
        Channel Number: 2
        ARA Level: 024
        Tracer: PHAL
        Injection Site: None
        Overlap Format: Grid
        Grid Size: 35
        (HEMISPHERE:COLUMN:ROW), GRID ONLY, OVERLAP, COLOR(S), REGION(S)
        (l:0:7), 30585, 40, 31:156:90|176:255:184|255:255:255, MOs_1|...
        (l:0:8), 30598, 27, 31:156:90|255:255:255, MOs_1|BORDER6
        (l:0:9), 30567, 58, 31:156:90|255:255:255, MOs_1|BORDER6
        """

        self.exp_overlap_csv_meta_dct = {
            'Project Name': 'SW010101-01A',
            'Case Name': 'SW010101-01A',
            'Slide Number': '1_09',
            'Channel Number': '2',
            'ARA Level': '024',
            'Tracer': 'PHAL',
            'Injection Site': 'None',
            'Overlap Format': 'Grid',
            'Grid Size': '35'}

        self.exp_overlap_csv_header_lst = [
            '(HEMISPHERE:COLUMN:ROW)', 'GRID ONLY', 'OVERLAP', 'COLOR(S)',
            'REGION(S)']

        self.exp_overlap_csv_rows = [
            ['(l:0:7)', '30585', '40', '31:156:90|176:255:184|255:255:255',
             'MOs_1|BORDER1|BORDER6'],
            ['(l:0:8)', '30598', '27', '31:156:90|255:255:255',
             'MOs_1|BORDER6'],
            ['(l:0:9)', '30567', '58', '31:156:90|255:255:255',
             'MOs_1|BORDER6']
        ]

        self.test_agg_overlap_csv_path = 'test_data/test_agg_overlap_csv.csv'
        """
        ARA Level,Atlas Name,Atlas Version,Case Name,Channel Number,...
        19,ARA,1,SW130212-02A,2,350,BLA_al,Grid,SW130212-02A,1_08,PHAL,(l:0:1),118286,4214,130:199:175|154:210:189|255:255:255,MOB_opl|border9|BORDER6
        19,ARA,1,SW130212-02A,2,350,BLA_al,Grid,SW130212-02A,1_08,PHAL,(l:0:2),119911,2589,130:199:173|130:199:174|130:199:175|130:199:176|154:210:189|255:255:255,MOB_mi|MOB_gl|MOB_opl|MOB_ipl|border9|BORDER6
        ...
        """

        self.exp_agg_overlap_csv_header_lst = [
            'ARA Level', 'Atlas Name', 'Atlas Version', 'Case Name',
            'Channel Number', 'Grid Size', 'Injection Site',
            'Overlap Format', 'Project Name', 'Slide Number', 'Tracer',
            '(HEMISPHERE:COLUMN:ROW)', 'GRID ONLY', 'OVERLAP', 'COLOR(S)',
            'REGION(S)']

        self.exp_agg_overlap_csv_two_rows = [
            ['19', 'ARA', '1', 'SW130212-02A', '2', '350', 'BLA_al', 'Grid',
             'SW130212-02A', '1_08', 'PHAL', '(l:0:1)', '118286', '4214',
             '130:199:175|154:210:189|255:255:255', 'MOB_opl|border9|BORDER6'],
            ['19', 'ARA', '1', 'SW130212-02A', '2', '350', 'BLA_al', 'Grid',
             'SW130212-02A', '1_08', 'PHAL', '(l:0:2)', '119911', '2589',
             '130:199:173|130:199:174|130:199:175|130:199:176|154:210:189'
             '|255:255:255', 'MOB_mi|MOB_gl|MOB_opl|MOB_ipl|border9|BORDER6']]

    def test_incl_excl_tup(self):
        roi_filter_csv_tup = cic_overlap.read_overlap_csv(self.roi_filter_csv)
        exp_incl_lst = sorted(['MRN', 'PAG', 'CUN'])
        exp_excl_lst = []
        (incl_lst, excl_lst) = \
            cic_overlap.incl_excl_tup(roi_filter_csv_tup=roi_filter_csv_tup,
                                      opairs_section='3_05')
        self.assertEqual(exp_incl_lst, sorted(incl_lst))
        self.assertEqual(exp_excl_lst, sorted(exp_excl_lst))

    def test_read_overlap_csv(self):
        (overlap_csv_meta_dct, overlap_csv_header_lst, overlap_csv_rows) = \
            cic_overlap.read_overlap_csv(self.test_overlap_csv_path)

        self.assertEqual(self.exp_overlap_csv_meta_dct, overlap_csv_meta_dct)
        self.assertEqual(self.exp_overlap_csv_header_lst,
                         overlap_csv_header_lst)
        self.assertEqual(self.exp_overlap_csv_rows, overlap_csv_rows)

    def test_write_overlap_csv(self):
        overlap_tup = (self.exp_overlap_csv_meta_dct,
                       self.exp_overlap_csv_header_lst,
                       self.exp_overlap_csv_rows)
        cic_overlap.write_overlap_csv(
            overlap_tup=overlap_tup,
            output_csv_path=self.test_write_overlap_csv_path)

        self.assertTrue(os.path.isfile(self.test_write_overlap_csv_path))

        (overlap_csv_meta_dct, overlap_csv_header_lst, overlap_csv_rows) = \
            cic_overlap.read_overlap_csv(self.test_write_overlap_csv_path)

        self.assertEqual(sorted(self.exp_overlap_csv_meta_dct.keys()),
                         sorted(overlap_csv_meta_dct.keys()))

        for key in self.exp_overlap_csv_meta_dct.keys():
            self.assertEqual(self.exp_overlap_csv_meta_dct[key],
                             overlap_csv_meta_dct[key])
        self.assertEqual(self.exp_overlap_csv_header_lst,
                         overlap_csv_header_lst)
        self.assertEqual(self.exp_overlap_csv_rows, overlap_csv_rows)
        os.remove(self.test_write_overlap_csv_path)

    def test_overlap_row(self):
        overlap_tup = cic_overlap.read_overlap_csv(self.test_overlap_csv_path)
        row_key_tup_lst = [('l', 0, 7), ('l', 0, 8), ('l', 0, 9)]

        for idx, row_key_tup in enumerate(row_key_tup_lst):
            row = cic_overlap.overlap_row(overlap_tup,
                                          hemi=row_key_tup[0],
                                          col=row_key_tup[1],
                                          row=row_key_tup[2])
            self.assertEqual(self.exp_overlap_csv_rows[idx], row)

    def test_read_agg_overlap_csv(self):
        (agg_overlap_csv_header_lst, agg_overlap_csv_rows) = \
            cic_overlap.read_agg_overlap_csv(self.test_agg_overlap_csv_path)

        self.assertEqual(self.exp_agg_overlap_csv_header_lst,
                         agg_overlap_csv_header_lst)
        self.assertEqual(self.exp_agg_overlap_csv_two_rows,
                         agg_overlap_csv_rows[0:2])
