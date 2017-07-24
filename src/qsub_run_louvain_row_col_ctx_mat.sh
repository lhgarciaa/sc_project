#!/bin/bash

if [ ! -n "$4" ]
then
    echo "Usage: `basename $0` <row-column-input-csv> <gamma> <num-runs> <venv-dir>"
    exit 1
fi

row_column_input_csv=$1;
gamma=$2;
num_runs=$3;
venv_dir=$4;

print_gamma=`printf "%.2f" $gamma`
root_dir=`dirname $row_column_input_csv`
mod_dir=$root_dir/mod-${print_gamma}
mkdir -p $mod_dir

# check if first task, if so then set param to write header to csv
wh=""
if [ "$SGE_TASK_ID" -eq "1" ]; then
    wh="-wh"
fi
   
. $venv_dir/bin/activate
name_base=`basename $row_column_input_csv` # for output file
python src/run_louvain_row_col_ctx_mat.py -v $wh -i $row_column_input_csv -g $gamma -r1 -ns 1 -o $mod_dir/out-${SGE_TASK_ID}_mod-${print_gamma}_runs-${num_runs}_$name_base

