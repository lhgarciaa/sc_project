#!/bin/bash
echoerr() { echo "$@" 1>&2; }
if [ ! -n "$4" ]
then
    echoerr "Usage: `basename $0` <ctx-mat-dir> <hdr-grep-val> <out-grep-val> <out-lbl>";
    exit 1
fi

ctx_mat_dir=$1
hdr_grep_val=$2
out_grep_val=$3
out_lbl=$4;

out_file=$ctx_mat_dir/c-$out_lbl.csv

if [ ! -d $ctx_mat_dir ]
then
    echoerr "ERROR: No connectivity matrix directory here $ctx_mat_dir";
    exit 1
fi

for file in `ls $ctx_mat_dir/m-*.csv`; do
    # write header if if file doesn't exist
    if [ ! -f $out_file ]
    then
	echo "Writing header to $out_file..."
	grep ^$hdr_grep_val $file > $out_file;
	echo "done. Now writing community lines"
    fi

    # write value
    grep ^$out_grep_val $file >> $out_file;
done
