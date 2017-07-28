#!/bin/bash

if [ ! -n "$2" ]
then
    echo "Usage: `basename $0` <wildcard> <venv-dir>"
    exit 1
fi

files=$1
venv_dir=$2

for file in $files
do
    qsub -cwd -q compute.q -l hostslots=1 src/qsub_char_cmt_str.sh $file $venv_dir
done


