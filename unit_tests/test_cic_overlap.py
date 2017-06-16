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
        (l:0:7), 30585, 40, 31:156:90|176:255:184|255:255:255, MOs_1|BORDER1|BORDER6
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


    def test_read_overlap_csv(self):
        (overlap_csv_meta_dct, overlap_csv_header_lst, overlap_csv_rows) = \
            cic_overlap.read_overlap_csv(self.test_overlap_csv_path)

        self.assertEqual(self.exp_overlap_csv_meta_dct, overlap_csv_meta_dct)
        self.assertEqual(self.exp_overlap_csv_header_lst,overlap_csv_header_lst)
        self.assertEqual(self.exp_overlap_csv_rows, overlap_csv_rows)
        
        
        
