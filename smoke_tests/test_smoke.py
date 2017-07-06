import unittest
import csv
import subprocess
import os
import filecmp


class RunSmokeTests(unittest.TestCase):
    def test_commands(self):
        csvreader = csv.reader

        # read smoke_tests.csv to get commands
        # smoke_tests.csv
        # COMMAND, OUTPUT_PATH, EXP_CONTENT_PATH
        # echo "hi there" > hi_there.txt, hi_there.txt, exp_hi_there.txt
        cmd_dct_lst = []
        with open('smoke_tests/smoke_tests.csv', 'rb') as csvfile:
            csvreader = csv.reader(csvfile)
            # header into dict
            for row_idx, row in enumerate(csvreader):
                # read header
                if row_idx == 0:
                    header_row = row
                    header_names = [x.strip() for x in header_row]

                else:
                    cmd_dct = {}
                    for col_idx, col in enumerate(row):
                        cmd_dct[header_names[col_idx]] = row[col_idx].strip()
                    cmd_dct_lst.append(cmd_dct)

        # go through each command, verify it generates output path as expected
        for cmd_dct in cmd_dct_lst:
            # execute the command
            # note, security risk with shell=True if third-party test execution
            subprocess.call(cmd_dct['COMMAND'], shell=True)

            # verify output file exists
            self.assertTrue(os.path.isfile(cmd_dct['OUTPUT_PATH']),
                            msg='\n\nThe command\n{}\ndid not generate '
                            'expected output\n{}\ncwd is {}\n'.
                            format(cmd_dct['COMMAND'], cmd_dct['OUTPUT_PATH'],
                                   os.getcwd()))

            # verify output file matches expected content
            self.assertTrue(os.path.isfile(cmd_dct['EXP_CONTENT_PATH']),
                            msg='"{}" not there\ncwd is {}'.format(
                                cmd_dct['EXP_CONTENT_PATH'],
                                os.getcwd()))

            subprocess.call(['dos2unix', '-q', cmd_dct['OUTPUT_PATH']])
            self.assertTrue(filecmp.cmp(cmd_dct['OUTPUT_PATH'],
                                        cmd_dct['EXP_CONTENT_PATH'],
                            shallow=False),
                            msg='files are not the same, run:\n'
                            'meld {} {}\nto view differences.'.
                            format(cmd_dct['EXP_CONTENT_PATH'],
                                   cmd_dct['OUTPUT_PATH']))

            os.remove(cmd_dct['OUTPUT_PATH'])
