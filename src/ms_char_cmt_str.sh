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
    name_base=`basename $file` # for output file
    logs_dir=qsub_logs
    log_name_base=$logs_dir/cc_${name_base}
    job_name=cc-$name_base
    qsub -N $job_name -cwd -q compute.q -o $log_name_base.out -e $log_name_base.err -l hostslots=1 src/qsub_char_cmt_str.sh $file $venv_dir
done


