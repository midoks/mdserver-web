#!/bin/sh

# cd /www/server/mdserver-web/plugins/op_waf/t && sh ngx_demo.sh

# cd /www/wwwroot/dev156.cachecha.com && sh ngx_demo.sh

pid=`ps -ef|grep openresty | grep -v grep | awk '{print $2}'`


# apt install linux-intel-iotg-5.15-tools-common
# apt install -y linux-tools-5.4.0-128-generic
# perf record -F 99 -p 790 -g -- sleep 60
perf record -F 99 -p $pid -g -- sleep 60


perf script -i perf.data &> perf.unfold
/opt/FlameGraph/stackcollapse-perf.pl perf.unfold &> perf.folded
/opt/FlameGraph/flamegraph.pl perf.folded > perf.svg