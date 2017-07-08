#!/bin/bash

if [ ! -n "$6" ]
then
    echo "Usage: `basename $0` <row-column-input-csv> <min-gamma> <max-gamma> <gamma-inc> <num-runs> <venv-dir>"
    exit 1
fi

row_column_input_csv=$1;
min_gamma=$2;
max_gamma=$3;
gamma_inc=$4;
num_runs=$5;
venv_dir=$6;

gamma=$min_gamma;
while (( $(echo "$gamma <= $max_gamma" | bc -l) )); do
    qsub -cwd -q compute.q -l hostslots=1 src/qsub_run_louvain_row_col_ctx_mat.sh $row_column_input_csv $gamma $num_runs $venv_dir
    gamma=$(echo "$gamma + $gamma_inc" | bc);
done;
 
