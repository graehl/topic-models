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
DEBUG=1 ${python:-python} $d/topics.py $d/topics-demo.py $d/test-topics.sh  -k 3 --topic-length 10 --quality 3
