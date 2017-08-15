#!/bin/bash

if [ ! -n "$4" ]; then
    echo "Usage: `basename $0` <row-column-input-csv> <gamma> <num-runs> <mod-dir>"
    exit 1
fi

row_column_input_csv=$1;
gamma=$2;
num_runs=$3;
mod_dir=$4;

name_base=`basename $row_column_input_csv` # for output file
print_gamma=`printf "%.2f" $gamma`
root_dir=`dirname $row_column_input_csv`
cat_file=$root_dir/m-${print_gamma}_runs-${num_runs}_$name_base
num_files_hdr=`ls -l $mod_dir | wc -l`
num_files=$((num_files_hdr - 1))

if [ $num_files -eq $num_runs ]; then
    echo "correct num files found"
    echo "concatenating $num_files files to $cat_file..."
    for i in $(seq 1 $num_runs); do
	cat $mod_dir/out-${i}_m-${print_gamma}_runs-${num_runs}_$name_base >> $cat_file;
    done;
    if [ -e $cat_file ]; then

	num_lines_hdr=`cat $cat_file | wc -l`
	num_lines=$((num_lines_hdr - 1))
	if [ "$num_lines" -eq "$num_runs" ]; then
	    echo "done";
	    echo "find pre-aggregated results in $mod_dir..."
	else
	    echo "ERROR: found $num_lines lines in $cat_file when looking for $num_runs"
	    echo "quitting"
	    exit 1
	fi	
    else
	echo "ERROR: did not find $cat_file"
	echo "quitting"
	exit 1
    fi
else
    echo "ERROR: found $num_files files in $mod_dir when looking for $num_runs"
    echo "quitting"
    exit 1
fi

