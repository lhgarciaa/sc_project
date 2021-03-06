#!/bin/bash

if [ ! -n "$5" ]
then
    echo "Usage: `basename $0` <roi-filter-csv> <case-dir> <grid-cell-size> <channel> <venv-dir>"
    exit 1
fi

roi_filter_csv=$1;
case_dir=$2;
grid_cell_size=$3;
channel=$4;
venv_dir=$5;

logs_dir=qsub_logs
mkdir -p $logs_dir # prepare logs file if it doesn't already exist
name_base=`basename $case_dir` # for output file
root_dir=`dirname $roi_filter_csv`

lvl=1
max_lvl=132
while (( $(echo "$lvl <= $max_lvl" | bc -l) )); do
    print_lvl=`printf "%0.3d" $lvl`
    log_name_base=$logs_dir/rf-${print_lvl}-${channel}-${name_base}
    job_name=rf${print_lvl}-${channel}-${name_base}
    qsub -N $job_name -cwd -o $log_name_base.out -e $log_name_base.err -q compute.q src/qsub_run_roi_filter_thresh_ovlp.sh $roi_filter_csv $case_dir $grid_cell_size $channel $lvl $venv_dir
    lvl=$(echo "$lvl + 1" | bc);
done;
