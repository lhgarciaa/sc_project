# general utilities related to
import csv
import os


def read_overlap_csv(input_csv_path):
    """
    Return an overlap csv

    Args:
        input_csv_path

    Returns:
       dict: dictionary with meta value key value pairs
       list: list of header labels
       list: list of rows in csv
    """
    meta_dct = {}
    header_lst = []
    rows = []

    assert os.path.isfile(input_csv_path)
    with open(input_csv_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile)
        num_metalines = 0
        for row_index, row in enumerate(csvreader):
            if row_index == 0 and len(row) == 1 and \
               row[0].split(':')[0] == 'Metalines':
                num_metalines = int(row[0].split(':')[1])

            elif row_index < num_metalines:
                assert len(row) == 1
                row_arr = row[0].split(':')
                meta_dct[row_arr[0].strip()] = row_arr[1].strip()
            elif row_index == num_metalines:
                header_lst = [col.strip() for col in row]

            else:
                rows.append([col.strip() for col in row])

    return (meta_dct, header_lst, rows)


def read_agg_overlap_csv(input_csv_path):
    """
    Return an agg overlap csv tuple

    Args:
        input_csv_path

    Returns:
       list: list of header labels
       list: list of rows in csv
    """
    header_lst = []
    rows = []
    # can simply call read_overlap_csv method and ignore meta_dct value
    tup = read_overlap_csv(input_csv_path=input_csv_path)
    (header_lst, rows) = tup[1:len(tup)]

    return (header_lst, rows)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
