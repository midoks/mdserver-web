#!/bin/sh
 

 # cd /www/server/mdserver-web/plugins/op_waf/t && sh ngx_debug.sh lua

if [ $# -ne 2 ]
then
    echo "Usage: ./`basename $0` lua/c NAME"
    exit
fi
 
pid=`ps -ef|grep openresty | grep -v grep | awk '{print $2}'`
name=$2


if [ ! -d /opt/openresty-systemtap-toolkit ];then
    cd /opt && git clone https://github.com/openresty/openresty-systemtap-toolkit
fi

if [ ! -d /opt/FlameGraph ];then
    cd /opt && git clone https://github.com/brendangregg/FlameGraph
fi
 
if [ $1 == "lua" ]; then
    /opt/openresty-systemtap-toolkit/ngx-sample-lua-bt -p $pid --luajit20 -t 30 >temp.bt
    /opt/openresty-systemtap-toolkit/fix-lua-bt temp.bt >${name}.bt
elif [ $1 == "c" ]; then
    /opt/nginx-systemtap-toolkit/sample-bt -p $pid -t 10 -u > ${name}.bt
else
    echo "type is only lua/c"
    exit
fi

/opt/FlameGraph/stackcollapse-stap.pl ${name}.bt >${name}.cbt
/opt/FlameGraph/flamegraph.pl ${name}.cbt >${name}.svg
rm -f temp.bt ${name}.bt ${name}.cbt

