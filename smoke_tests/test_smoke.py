import unittest
import csv
import subprocess
import os
import filecmp
import time
import random


def randomly(lst):
    assert type(lst) == list
    random.shuffle(lst)
    return iter(lst)


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
            comment = None  # init to None, set to comment text if found
            for row_idx, row in enumerate(csvreader):
                # read header
                if row_idx == 0:
                    header_row = row
                    header_names = [x.strip() for x in header_row]

                elif row[0].strip().startswith('#'):
                    comment = row[0].strip()

                else:
                    cmd_dct = {}
                    for col_idx, col in enumerate(row):
                        cmd_dct[header_names[col_idx]] = row[col_idx].strip()
                    if comment is not None:
                        cmd_dct['COMMENT'] = comment
                        comment = None
                    cmd_dct_lst.append(cmd_dct)

        # go through each command, verify it generates output path as expected
        for cmd_dct in randomly(cmd_dct_lst):
            # if comment then print it
            if 'COMMENT' in cmd_dct:
                print("\n{}".format(
                    cmd_dct['COMMENT'][2:len(cmd_dct['COMMENT'])]))

            # execute the command
            # note, security risk with shell=True
            start = time.time()
            print("CALLING\n{}".format(cmd_dct['COMMAND']))
            subprocess.call(cmd_dct['COMMAND'], shell=True)
            print("completed in {:0.2f}s\n".
                  format(time.time() - start))

            # verify output file exists
            output_path_lst = cmd_dct['OUTPUT_PATH'].split()
            for output_path in output_path_lst:
                self.assertTrue(os.path.isfile(output_path),
                                msg='\n\nThe command\n{}\ndid not generate'
                                ' expected output\n{}\ncwd is {}\n'.
                                format(cmd_dct['COMMAND'],
                                       output_path,
                                       os.getcwd()))

            # verify output file matches expected content
            exp_content_path_lst = cmd_dct['EXP_CONTENT_PATH'].split()
            for exp_content_path in exp_content_path_lst:
                self.assertTrue(os.path.isfile(exp_content_path),
                                msg='"{}" not there\ncwd is {}'.format(
                                    exp_content_path,
                                    os.getcwd()))
            for idx, output_path in enumerate(output_path_lst):
                exp_content_path = exp_content_path_lst[idx]
                if ".csv" in output_path:
                    subprocess.call(['dos2unix', '-q', output_path])
                self.assertTrue(filecmp.cmp(output_path,
                                            exp_content_path,
                                            shallow=False),
                                msg='files are not the same, run:\n'
                                'meld {} {}\nto view differences.'.
                                format(exp_content_path,
                                       output_path))

            for idx, output_path in enumerate(output_path_lst):
                os.remove(output_path)
