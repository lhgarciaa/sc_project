# CIC utilities typically related to i/o
import os
import sys


def pickle_path(input_path):
    basename = os.path.basename(input_path)
    ext = os.path.splitext(input_path)[1]
    new_basename = '.' + basename.replace(ext, '.p')
    return input_path.replace(basename, new_basename)


def pickle_dct(parser_args):
    pickle_dct = parser_args
    pickle_dct['script'] = sys.argv[0]
    pickle_dct['cwd'] = os.getcwd()

    return pickle_dct
