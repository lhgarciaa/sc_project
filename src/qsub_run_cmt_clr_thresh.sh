#!/bin/bash

if [ ! -n "$7" ]
then
    echo 'Usage: `basename $0` <char-cmt-str-csv> <case-dir> <grid-cell-size> <channel> <level> "<inj-site-order>" <venv-dir>'
    exit 1
fi

char_cmt_str_csv=$1;
case_dir=$2;
grid_cell_size=$3;
channel=$4;
lvl=$5
inj_site_order=$6
venv_dir=$7

print_lvl=`printf "%0.3d" $lvl`

. $venv_dir/bin/activate
python src/cmt_clr_thresh.py -v -i $char_cmt_str_csv -cd $case_dir -gcs $grid_cell_size -ch $channel -lvl $lvl -iso $inj_site_order
