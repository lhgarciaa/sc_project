import unittest
from src import cic_overlap


class TestCicOverlap(unittest.TestCase):
    def setUp(self):
        self.test_overlap_csv_path = 'test_data/test_overlap_csv.csv'
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

    def test_read_overlap_csv(self):
        (overlap_csv_meta_dct, overlap_csv_header_lst, overlap_csv_rows) = \
            cic_overlap.read_overlap_csv(self.test_overlap_csv_path)

        self.assertEqual(self.exp_overlap_csv_meta_dct, overlap_csv_meta_dct)
        self.assertEqual(self.exp_overlap_csv_header_lst,
                         overlap_csv_header_lst)
        self.assertEqual(self.exp_overlap_csv_rows, overlap_csv_rows)

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
