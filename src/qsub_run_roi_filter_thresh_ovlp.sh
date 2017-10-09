#!/bin/bash

if [ ! -n "$6" ]
then
    echo "Usage: `basename $0` <roi-filter-csv> <case-dir> <grid-cell-size> <channel> <level> <venv-dir>"
    exit 1
fi

roi_filter_csv=$1;
case_dir=$2;
grid_cell_size=$3;
channel=$4;
lvl=$5
venv_dir=$6

print_lvl=`printf "%0.3d" $lvl`

. $venv_dir/bin/activate
python src/roi_filter_thresh_ovlp.py -v -ic $roi_filter_csv -cd $case_dir -gcs $grid_cell_size -ch $channel -lvl $lvl
