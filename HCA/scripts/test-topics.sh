O=docs
rm -f $O.*
rm -f *.$O.*
set -e
d=`dirname $0`
wp=$d/wp.1000.txt
if ! [[ -f $wp ]] ; then
    wp=
fi
set -x
DEBUG=1 python $d/topics.py *.py *.pl -k 10 --topic-length 8
