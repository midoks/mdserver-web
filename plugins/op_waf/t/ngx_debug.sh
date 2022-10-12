#!/bin/sh
 

# cd /www/server/mdserver-web/plugins/op_waf/t && sh ngx_debug.sh lua t1
# cd /www/server/mdserver-web/plugins/op_waf/t && sh ngx_debug.sh c t2

if [ $# -ne 2 ]
then
    echo "Usage: ./`basename $0` lua/c NAME"
    exit
fi
 
pid=`ps -ef|grep openresty | grep -v grep | awk '{print $2}'`
name=$2



# /opt/openresty-systemtap-toolkit/ngx-active-reqs -p 496435

# /opt/openresty-systemtap-toolkit/sample-bt -p 496435 -t 5 -k > a.bt



if [ ! -d /opt/openresty-systemtap-toolkit ];then
    cd /opt && git clone https://github.com/openresty/openresty-systemtap-toolkit
fi

if [ ! -d /opt/FlameGraph ];then
    cd /opt && git clone https://github.com/brendangregg/FlameGraph
fi
 
if [ $1 == "lua" ]; then
    # /opt/openresty-systemtap-toolkit/ngx-sample-lua-bt -p 496435 --luajit21 -t 30 >temp.bt
    /opt/openresty-systemtap-toolkit/ngx-sample-lua-bt -p $pid --luajit20 -t 30 >temp.bt
    # /opt/openresty-systemtap-toolkit/fix-lua-bt temp.bt >t1.bt
    /opt/openresty-systemtap-toolkit/fix-lua-bt temp.bt >${name}.bt
elif [ $1 == "c" ]; then
    # /opt/openresty-systemtap-toolkit/sample-bt -p 496435 -t 10 -u > t2.bt
    /opt/openresty-systemtap-toolkit/sample-bt -p $pid -t 10 -u > ${name}.bt
else
    echo "type is only lua/c"
    exit
fi



# /opt/FlameGraph/stackcollapse-perf.pl perf.unfold &> perf.folded
# /opt/FlameGraph/flamegraph.pl perf.folded > perf.svg

/opt/FlameGraph/stackcollapse-stap.pl ${name}.bt >${name}.cbt
/opt/FlameGraph/flamegraph.pl ${name}.cbt >${name}.svg
rm -f temp.bt ${name}.bt ${name}.cbt

