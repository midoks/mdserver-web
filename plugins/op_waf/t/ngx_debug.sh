#!/bin/sh
export PATH=$PATH:/opt/stapxx

# https://moonbingbing.gitbooks.io/openresty-best-practices/content/flame_graph/install.html
# apt install elfutils
# sudo apt-get install -y systemtap gcc
# sudo apt-get install linux-headers-generic gcc libcap-dev
# apt-get install -y libdw-dev
# apt-get install -y fakeroot build-essential crash kexec-tools makedumpfile kernel-wedge kernel-package
# apt-get install -y git-core libncurses5 libncurses5-dev libelf-dev asciidoc binutils-dev
# apt-get build-dep linux

# cat > /etc/apt/sources.list.d/ddebs.list << EOF
# deb http://ddebs.ubuntu.com/ precise main restricted universe multiverse
# EOF
# 
# apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ECDCAD72428D7C01
# apt-get update

if [ $# -ne 2 ]
then
    echo "Usage: ./`basename $0` lua/c NAME"
    exit
fi
 
pid=`ps -ef|grep openresty | grep -v grep | awk '{print $2}'`
name=$2


# /opt/openresty-systemtap-toolkit/ngx-active-reqs -p 496435
# /opt/openresty-systemtap-toolkit/sample-bt -p 496435 -t 5 -k > a.bt
# kernel-debuginfo-common kernel-debuginfo
# apt install -y kernel-debuginfo-common kernel-debuginfo
# apt install -y kernel-*



# /opt/stapxx/samples/lj-lua-stacks.sxx --arg time=5 --skip-badvars -x 314532  > tmp.bt


if [ ! -d /opt/openresty-systemtap-toolkit ];then
    cd /opt && git clone https://github.com/openresty/openresty-systemtap-toolkit
fi

if [ ! -d /opt/stapxx ];then
    cd /opt && git clone https://github.com/openresty/stapxx
fi

# dpkg -i --force-overwrite /var/cache/apt/archives/linux-tools-common_5.4.0-128.144_all.deb


if [ ! -d /opt/FlameGraph ];then
    cd /opt && git clone https://github.com/brendangregg/FlameGraph
fi
 
if [ $1 == "lua" ]; then
    # /opt/openresty-systemtap-toolkit/ngx-sample-lua-bt -p 45266 --luajit20 -t 30 >temp.bt
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

