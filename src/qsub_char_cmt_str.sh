if [ ! -n "$2" ]
then
    echo "Usage: `basename $0` <file> <venv-dir>"
    exit 1
fi

file=$1
venv_dir=$2

. $venv_dir/bin/activate
basepath=`basename $file`
dirname=`dirname $file`
out_file="$dirname/char_cmt_str_$basepath"
if [ ! -f "$out_file" ]
then
    cmd="python src/char_cmt_str.py -v -i $file -H" 
    $cmd > $out_file
fi
