#!/bin/bash

if [ ! -n "$6" ]
then
    echo 'Usage: `basename $0` <case-basedir> "<case-ch-tups>" <grid-cell-size> <level> <output-dir> <venv-dir>'
    exit 1
fi

case_basedir=$1
case_ch_tups=$2
grid_cell_size=$3
lvl=$4
output_dir=$5
venv_dir=$6

print_lvl=`printf "%0.3d" $lvl`

. $venv_dir/bin/activate
python src/agg_cmt_clr_thresh.py -v -cb $case_basedir -cct $case_ch_tups -gcs $grid_cell_size -lvl $lvl -od $output_dir -aa
