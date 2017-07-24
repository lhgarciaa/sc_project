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

logs_dir=qsub_logs
mkdir -p $logs_dir # prepare logs file if it doesn't already exist
name_base=`basename $row_column_input_csv` # for output file

gamma=$min_gamma;
while (( $(echo "$gamma <= $max_gamma" | bc -l) )); do
    print_gamma=`printf "%.2f" $gamma`
    log_name_base=$logs_dir/mod-${print_gamma}_runs-${num_runs}_${name_base}
    log_name_cat=$logs_dir/cat_mod-${print_gamma}_runs-${num_runs}_${name_base}
    job_name=job_mod-$gamma
    qsub -N $job_name -cwd -t 1-$num_runs -o $log_name_base.out -e $log_name_base.err -q compute.q src/qsub_run_louvain_row_col_ctx_mat.sh $row_column_input_csv $gamma $num_runs $venv_dir
    qsub -hold_jid $job_name -cwd -o $log_name_cat.out -e $log_name_cat.err -q compute.q src/qsub_concat_louvain.sh $row_column_input_csv $gamma $num_runs
    gamma=$(echo "$gamma + $gamma_inc" | bc);
done;
 
