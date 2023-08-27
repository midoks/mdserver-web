#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
SYS_ARCH=`arch`

# apt-get install linux-perf
# apt-get update -y
# strace -p $(ps -ef|grep "pool www" | awk '{print $2}' | grep -v grep | tr '\n' ',' )

# perf record -F 99 -p 2401699 -g -- sleep 30
# perf script > out.perf
# /www/server/dynamic-tracking/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# /www/server/dynamic-tracking/FlameGraph/flamegraph.pl out.folded > php-zend-flame-graph.svg

# WWW_PID=$(ps -ef|grep "pool www" | awk '{print $2}' | grep -v grep | tr '\n' ',')
# WWW_PID=${WWW_PID//,/}
# WWW_PID=${var%,}
# perf record -F 99 -p "1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,1050,1051,1127,1128,1129,1130,1131,1473,1768,2848,2962,21582,35891" \
# -g -- sleep 30