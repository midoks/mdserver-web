#!/bin/sh

# cd /www/server/mdserver-web/plugins/op_waf/t && sh ngx_demo.sh
# cd /www/wwwroot/dev156.cachecha.com && sh ngx_demo.sh


# only openresty
# pid=`ps -ef|grep openresty | grep -v grep | awk '{print $2}'`
# perf record -F 99 -p $pid -g -- sleep 60


#全部
perf record -F 99  -g  -a  -- sleep 60 


perf script -i perf.data &> perf.unfold
/opt/FlameGraph/stackcollapse-perf.pl perf.unfold &> perf.folded
/opt/FlameGraph/flamegraph.pl perf.folded > perf.svg