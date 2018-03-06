#!/bin/bash

if [ ! -n "$5" ]
then
    echo 'Usage: `basename $0` <case-basedir> "<case-ch-tups>" <grid-cell-size> <output-dir> <venv-dir>'
    exit 1
fi

case_basedir=$1;
case_ch_tups=$2;
grid_cell_size=$3;
output_dir=$4
venv_dir=$5;

logs_dir=qsub_logs
mkdir -p $logs_dir # prepare logs file if it doesn't already exist
name_base=`basename $case_basedir`

lvl=1
max_lvl=132
while (( $(echo "$lvl <= $max_lvl" | bc -l) )); do
    print_lvl=`printf "%0.3d" $lvl`
    log_name_base=$logs_dir/acc-${print_lvl}-${name_base}
    job_name=acc-${print_lvl}-${name_base}
    qsub -N $job_name -cwd -o $log_name_base.out -e $log_name_base.err -q compute.q src/qsub_run_agg_cmt_clr_thresh.sh $case_basedir "$case_ch_tups" $grid_cell_size $lvl $output_dir $venv_dir
    lvl=$(echo "$lvl + 1" | bc);
done;
