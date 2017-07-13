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

. $venv_dir/bin/activate
python src/run_louvain_row_col_ctx_mat.py -v -i $row_column_input_csv -g $gamma -r 1 -ns 1 

