#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


# debug
# cd /www/server/mdserver-web
# bash /www/server/mdserver-web/plugins/dynamic-tracking/shell/simple_trace.sh "2401699"


curPath=`pwd`
rootPath=$(dirname "$curPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
PID=$1

echo $rootPath # /Users/midoks/Desktop/mwdev/server
echo $curPath # /Users/midoks/Desktop/mwdev/server/mdserver-web

APP_DIR=/www/server/dynamic-tracking
DST_FILE_DIR=${APP_DIR}/trace/PID_${PID}
mkdir -p $DST_FILE_DIR

# DST_FILE=${DST_FILE_DIR}/main.strace

# perf record -F 99 -p 335584 -g -- sleep 30

cd ${DST_FILE_DIR}
perf record -F 99 -p ${PID} -g -- sleep 30

perf script > out.perf
${APP_DIR}/FlameGraph/stackcollapse-perf.pl ${DST_FILE_DIR}/out.perf > ${DST_FILE_DIR}/out.folded
${APP_DIR}/FlameGraph/flamegraph.pl ${DST_FILE_DIR}/out.folded > ${DST_FILE_DIR}/main.svg

# perf record -F 99 -p 2401699 -g -- sleep 30
# perf script > out.perf
# /www/server/dynamic-tracking/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# /www/server/dynamic-tracking/FlameGraph/flamegraph.pl out.folded > php-zend-flame-graph.svg

# ${APP_DIR}/FlameGraph/stackcollapse.pl $DST_FILE > ${DST_FILE_DIR}/kernel.cbt
# ${APP_DIR}/FlameGraph/flamegraph.pl ${DST_FILE_DIR}/kernel.cbt > ${DST_FILE_DIR}/main.svg

