#!/bin/bash

if [ ! -n "$6" ]
then
    echo 'Usage: `basename $0` <char-cmt-str-csv> <case-dir> <grid-cell-size> <channel> "<inj-site-order>" <venv-dir>'
    exit 1
fi

char_cmt_str_csv=$1;
case_dir=$2;
grid_cell_size=$3;
channel=$4;
inj_site_order=$5
venv_dir=$6;

logs_dir=qsub_logs
mkdir -p $logs_dir # prepare logs file if it doesn't already exist
name_base=`basename $case_dir` # for output file

lvl=1
max_lvl=132
while (( $(echo "$lvl <= $max_lvl" | bc -l) )); do
    print_lvl=`printf "%0.3d" $lvl`
    log_name_base=$logs_dir/cc-${print_lvl}-${channel}-${name_base}
    job_name=cc${print_lvl}-${channel}-${name_base}
    qsub -N $job_name -cwd -o $log_name_base.out -e $log_name_base.err -q compute.q src/qsub_run_cmt_clr_thresh.sh $char_cmt_str_csv $case_dir $grid_cell_size $channel $lvl "$inj_site_order" $venv_dir
    lvl=$(echo "$lvl + 1" | bc);
done;
