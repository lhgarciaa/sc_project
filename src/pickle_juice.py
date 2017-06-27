from __future__ import print_function
import argparse
import cPickle as pickle
import os
import glob
import shutil
import cic_utils


def main():
    parser = argparse.ArgumentParser(
        description="Reproducability friendly code, manages data and arguments"
        " used to generate it")
    parser.add_argument('-co', '--corresponding_output',
                        help="Path to output of (typically image) data"
                        " corresponding to pickle",
                        required=True)

    parser.add_argument('-pa', '--print_args',
                        help="Print command line arguments used to produce "
                        "corresponding output",
                        action='store_true')

    parser.add_argument('-cpp', '--copy_path',
                        help='Directory to copy corresponding output and '
                        'argument pickle dict',
                        default=False)
    parser.add_argument('-v', '--verbose',
                        help='Print matrix, cluster related output',
                        action='store_true')

    # required args, and derivitives
    args = vars(parser.parse_args())
    corresponding_output_wildcard = args['corresponding_output']

    # optional args
    print_args = args['print_args']
    copy_path = args['copy_path']
    verbose = args['verbose']

    for corresponding_output in glob.glob(corresponding_output_wildcard):
        pickle_path = cic_utils.pickle_path(corresponding_output)

        if not copy_path:
            print_args = True

        if os.path.isfile(pickle_path):
            p = pickle.load(open(pickle_path, "rb"))

            assert p, 'Problem reading {}'.format(pickle_path)

            if print_args:
                if 'cwd' in p and 'script' in p:
                    print("\nTo generate {}:\n".
                          format(os.path.basename(corresponding_output)))
                    print("cd {} &&".format(p.pop('cwd')))
                    print("python {} ".format(p.pop('script')), end='')
                for arg in p:
                    if p[arg] is None:
                        print("", end=' ')

                    elif type(p[arg]) == bool and p[arg]:
                        # note this only works for action='store_true'
                        print("--{}".format(arg), end=' ')

                    elif type(p[arg]) == bool and not p[arg]:
                        # note this only works for action='store_true'
                        print("", end=' ')

                    elif type(p[arg]) == str and ' ' in p[arg]:
                        print('--{}="{}"'.format(arg, p[arg]), end=' ')

                    else:
                        print("--{}={}".format(arg, p[arg]), end=' ')
                print("&&\ncd -\n")

            if copy_path:
                assert(os.path.isdir(copy_path))
                if verbose:
                    print("copying {} to {}".
                          format(corresponding_output, copy_path))
                shutil.copy2(corresponding_output, copy_path)
                if verbose:
                    print("copying {} to {}".
                          format(pickle_path, copy_path))
                shutil.copy2(pickle_path, copy_path)
        else:
            print("WARNING: No pickle path {} found for {}".
                  format(pickle_path, corresponding_output))


if __name__ == '__main__':
    main()
