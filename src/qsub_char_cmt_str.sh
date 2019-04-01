if [ ! -n "$3" ]
then
    echo "Usage: `basename $0` <file> <inj-sites> <venv-dir>"
    exit 1
fi

file=$1
inj_sites=$2
venv_dir=$3

. $venv_dir/bin/activate
basepath=`basename $file`
dirname=`dirname $file`
out_file="$dirname/char_cmt_str_$basepath"
if [ ! -f "$out_file" ]
then
    cmd="python src/char_cmt_str.py -v -i $file -H -isl $inj_sites"
    $cmd > $out_file
else
    echo "$out_file exists, skipping char cmt run"
fi
