#!/bin/bash
echoerr() { echo "$@" 1>&2; }
if [ ! -n "$3" ]
then
    echoerr "Usage: `basename $0` <case-dir> <dest-dir> <channel-num>"
    exit 1
fi

case_dir=$1
dest_dir=$2
channel_num=$3

if [ -e $case_dir ]; then
    case_name=`basename $case_dir`
    src_opairs_path=$case_dir/opairs.lst
    dest_case_dir=$dest_dir/$case_name
    dest_opairs_path=$dest_case_dir/opairs.lst

    if [ -e $src_opairs_path ]; then
	if [ -e $dest_opairs_path ]; then
	    read -p "WARNING: $dest_opairs_path exists, continue? (Y/N) " yn
	    case ${yn:0:1} in
		y|Y ) echo "Copying $src_opairs_path to $dest_opairs_path"
		      cp $src_opairs_path $dest_opairs_path
		      ;;
		* ) exit 0;;
	    esac
	else
	    mkdir -p $dest_case_dir
	    echo "Copying $src_opairs_path to $dest_opairs_path"
	    cp $src_opairs_path $dest_opairs_path
	fi

    else
	echoerr "ERROR: $src_opairs_path not found"
    fi

    src_thresh_dir=$case_dir/threshold/channels/$channel_num
    dest_thresh_dir=$dest_dir/$case_name/threshold/channels/$channel_num

    if [ -e $src_thresh_dir ]; then
	echo "Making $dest_thresh_dir"
	mkdir -p $dest_thresh_dir
	echo "Copying tifs from $src_thresh_dir"
	cp $src_thresh_dir/*.tif $dest_thresh_dir
    else
	echoerr "ERROR: threshold directory '$src_thresh_dir' not found"
    fi

    src_ovlp_dir=$case_dir/overlap/$channel_num
    dest_ovlp_dir=$dest_dir/$case_name/overlap/$channel_num

    if [ -e $src_ovlp_dir ]; then
	echo "Making $dest_ovlp_dir"
	mkdir -p $dest_ovlp_dir
	echo "Copying csvs from $src_ovlp_dir"
	cp $src_ovlp_dir/*.csv $dest_ovlp_dir
    else
	echoerr "ERROR: overlap directory '$src_ovlp_dir' not found"
    fi

else
    echoerr "ERROR: case directory '$case_dir' not found"
fi
