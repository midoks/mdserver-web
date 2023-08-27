#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


# debug
# cd /www/server/mdserver-web
# bash /www/server/mdserver-web/plugins/dynamic-tracking/shell/simple_macosx_trace.sh "22431"

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web
# bash /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/dynamic-tracking/shell/simple_macosx_trace.sh "22431"

# dtrace -x ustackframes=100 -n 'pid$target::mach_msg_trap:entry { @[ustack()] = count(); } tick-30s { exit(0); }' -p 18572 -o out.SystemUIServer_stacks
# /Users/midoks/Desktop/mwdev/server/dynamic-tracking/FlameGraph/stackcollapse.pl out.SystemUIServer_stacks > kernel.cbt
# /Users/midoks/Desktop/mwdev/server/dynamic-tracking/FlameGraph/flamegraph.pl kernel.cbt > kernel.svg

curPath=`pwd`
rootPath=$(dirname "$curPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
PID=$1

echo $rootPath # /Users/midoks/Desktop/mwdev/server
echo $curPath # /Users/midoks/Desktop/mwdev/server/mdserver-web

APP_DIR=${rootPath}/dynamic-tracking
DST_FILE_DIR=${APP_DIR}/trace/PID_${PID}
mkdir -p $DST_FILE_DIR

DST_FILE=${DST_FILE_DIR}/out.SystemUIServer_stacks

if [ ! -f $DST_FILE ];then
	sudo dtrace -x ustackframes=100 -n 'pid$target::mach_msg_trap:entry { @[ustack()] = count(); } tick-30s { exit(0); }' -p "$PID" -o $DST_FILE
fi

${APP_DIR}/FlameGraph/stackcollapse.pl $DST_FILE > ${DST_FILE_DIR}/kernel.cbt
${APP_DIR}/FlameGraph/flamegraph.pl ${DST_FILE_DIR}/kernel.cbt > ${DST_FILE_DIR}/main.svg

