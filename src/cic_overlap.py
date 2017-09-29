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

    assert os.path.isfile(input_csv_path), "No overlap csv {}".format(
        input_csv_path)
    with open(input_csv_path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile)
        num_metalines = 0
        for row_index, row in enumerate(csvreader):
            if row_index == 0 and row[0].split(':')[0].lower() == 'metalines':
                num_metalines = int(row[0].split(':')[1])

            elif row_index < num_metalines:
                row_arr = row[0].split(':')
                meta_dct[row_arr[0].strip()] = row_arr[1].strip()
            elif row_index == num_metalines:
                header_lst = [col.strip() for col in row]

            else:
                rows.append([col.strip() for col in row])

    return (meta_dct, header_lst, rows)


# format and write overlap csv
def write_overlap_csv(overlap_tup, output_csv_path):
    (meta_dct, header_lst, rows) = overlap_tup
    with open(output_csv_path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Metalines: {}'.format(
            len(meta_dct.keys()) + 1)])
        for key in meta_dct.keys():
            csvwriter.writerow(['{}: {}'.format(key, meta_dct[key])])
        csvwriter.writerow(header_lst)
        for row in rows:
            csvwriter.writerow(row)


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


# return row from overlap corresponding to hemi, column row, None if not found
def overlap_row(overlap_tup, hemi, col, row):
    # assert that column header is as expected
    (meta_dct, header_lst, overlap_rows) = overlap_tup
    tup_col = 0
    assert header_lst[tup_col] == '(HEMISPHERE:COLUMN:ROW)', \
        "Uh-oh, header column {} overlap file is nor formatted as required".\
        format(header_lst[tup_col])

    key = '({}:{}:{})'.format(hemi, col, row)
    # find row containing key in first column and return that
    for overlap_row in overlap_rows:
        if overlap_row[tup_col] == key:
            return overlap_row

    # no row found
    return None


# returns true if either overlap ROIs in incl_lst or ROIs not in excl_lst
def should_incl_not_excl(header_lst, overlap_row, incl_lst, excl_lst):
    assert len(incl_lst) == 0 or len(excl_lst) == 0, \
        "Currently only support include or exclude lst but {}/{}".format(
            incl_lst, excl_lst)
    regions_col = 4
    assert header_lst[regions_col].strip() == "REGION(S)", \
        "Uh-oh, header column {} overlap file is nor formatted as required".\
        format(header_lst[regions_col])
    regions = overlap_row[regions_col].split('|')
    if len(incl_lst) > 0:
        for region in regions:
            if region in incl_lst:
                return True
        # if no region was in inclusion list, then return false
        return False
    if len(excl_lst) > 0:
        for region in regions:
            if region in excl_lst:
                return False
        # if no region in exclusion list, then return true
        print "returning true because no {} in {}".format(regions,
                                                          excl_lst)
        return True
    # if no inclusion or exclusion list, then return true
    return True


def incl_excl_tup(roi_filter_csv_tup, opairs_section):
    section_col = 0
    include_col = 1
    exclude_col = 2

    incl_lst = []
    excl_lst = []
    (meta_dct, header_lst, incl_excl_rows) = roi_filter_csv_tup

    assert header_lst[section_col].strip().lower() == "section", \
        "{} != SECTION".format(header_lst[section_col])
    assert header_lst[include_col].strip().lower() == "include"
    assert header_lst[exclude_col].strip().lower() == "exclude"

    for incl_excl_row in incl_excl_rows:
        if incl_excl_row[section_col].strip() in opairs_section.strip():
            incl_lst = incl_excl_row[include_col].split()
            excl_lst = incl_excl_row[exclude_col].split()
    return (incl_lst, excl_lst)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
