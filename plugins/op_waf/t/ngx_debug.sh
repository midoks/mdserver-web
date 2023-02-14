#!/bin/sh
export PATH=$PATH:/opt/stap/bin:/opt/stapxx

# cd /www/server/mdserver-web/plugins/op_waf/t && bash ngx_debug.sh lua ok
# cd /www/server/mdserver-web/plugins/op_waf/t && bash ngx_debug.sh c ok


if [ ${_os} == "Darwin" ]; then
    OSNAME='macos'
elif grep -Eq "openSUSE" /etc/*-release; then
    OSNAME='opensuse'
    zypper refresh
    zypper install cron wget curl zip unzip
elif grep -Eq "FreeBSD" /etc/*-release; then
    OSNAME='freebsd'
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
    OSNAME='rhel'
    yum install -y wget curl zip unzip tar crontabs
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
    OSNAME='fedora'
    yum install -y wget curl zip unzip tar crontabs
elif grep -Eqi "Rocky" /etc/issue || grep -Eq "Rocky" /etc/*-release; then
    OSNAME='rhel'
    yum install -y wget curl zip unzip tar crontabs
elif grep -Eqi "AlmaLinux" /etc/issue || grep -Eq "AlmaLinux" /etc/*-release; then
    OSNAME='rhel'
    yum install -y wget curl zip unzip tar crontabs
elif grep -Eqi "Amazon Linux" /etc/issue || grep -Eq "Amazon Linux" /etc/*-release; then
    OSNAME='amazon'
    yum install -y wget curl zip unzip tar crontabs
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/os-release; then
    OSNAME='debian'
    apt update -y
    apt install -y wget curl zip unzip tar cron
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/os-release; then
    OSNAME='ubuntu'
    apt update -y
    apt install -y wget curl zip unzip tar cron
else
    OSNAME='unknow'
fi


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
 
pids=`ps -ef|grep nginx | grep -v grep | awk '{print $2}'`
name=$2


# /opt/openresty-systemtap-toolkit/ngx-active-reqs -p 496435
# /opt/openresty-systemtap-toolkit/sample-bt -p 496435 -t 5 -k > a.bt
# kernel-debuginfo-common kernel-debuginfo
# apt install -y kernel-debuginfo-common kernel-debuginfo
# apt install -y kernel-*

if [ "$OSNAME" == "debian" ];then
    apt install  -y systemtap
    apt-get install -y build-essential 
    apt-get install -y linux-headers-$(uname -r)
elif [ "$OSNAME" == "centos" ];then
    yum install -y kernel-devel-$(uname -r)
fi

# /opt/stapxx/samples/lj-lua-stacks.sxx --arg time=5 --skip-badvars -x 45266  > tmp.bt


if [ ! -d /opt/openresty-systemtap-toolkit ];then
    cd /opt && git clone https://github.com/openresty/openresty-systemtap-toolkit
fi

if [ ! -d /opt/stapxx ];then
    cd /opt && git clone https://github.com/openresty/stapxx
fi

# stap++ -I ./tapset -x 45266 --arg limit=10 samples/ngx-upstream-post-conn.sxx
# dpkg -i --force-overwrite /var/cache/apt/archives/linux-tools-common_5.4.0-128.144_all.deb

# /opt/openresty-systemtap-toolkit/ngx-active-reqs -p 45266

# git clone git://sourceware.org/git/systemtap.git
# ./configure --prefix=/opt/stap --disable-docs --disable-publican --disable-refdocs CFLAGS="-g -O2"

if [ ! -d /opt/FlameGraph ];then
    cd /opt && git clone https://github.com/brendangregg/FlameGraph
fi
 
for pid in ${pids[@]}; do
    echo "strace:$pid"
    if [ $1 == "lua" ]; then
        # --without-luajit-gc64 | lua 模式编译时需要使用此参数
        /opt/openresty-systemtap-toolkit/ngx-sample-lua-bt -p $pid --luajit20 -t 30 >temp.bt
        /opt/openresty-systemtap-toolkit/fix-lua-bt temp.bt >${name}_${pid}.bt
    elif [ $1 == "c" ]; then
        /opt/openresty-systemtap-toolkit/sample-bt -p $pid -t 10 -u > ${name}_${pid}.bt
    else
        echo "type is only lua/c"
        exit
    fi

    /opt/FlameGraph/stackcollapse-stap.pl ${name}_${pid}.bt >${name}_${pid}.cbt
    /opt/FlameGraph/flamegraph.pl ${name}_${pid}.cbt >${name}_${pid}.svg
    rm -f temp.bt ${name}_${pid}.bt ${name}_${pid}.cbt
    echo "strace:$pid, end!"
    echo "${name}_${pid}.svg -- make ok"
done

# if [ $1 == "lua" ]; then
#     # /opt/openresty-systemtap-toolkit/ngx-sample-lua-bt -p 377452 --luajit20 -t 30 >temp.bt
#     /opt/openresty-systemtap-toolkit/ngx-sample-lua-bt -p $pid --luajit20 -t 30 >temp.bt
#     # /opt/openresty-systemtap-toolkit/fix-lua-bt temp.bt >t1.bt
#     /opt/openresty-systemtap-toolkit/fix-lua-bt temp.bt >${name}.bt
# elif [ $1 == "c" ]; then
#     # /opt/openresty-systemtap-toolkit/sample-bt -p 496435 -t 10 -u > t2.bt
#     /opt/openresty-systemtap-toolkit/sample-bt -p $pid -t 10 -u > ${name}.bt
# else
#     echo "type is only lua/c"
#     exit
# fi


# # debuginfo-install kernel-3.10.0-1160.80.1.el7.x86_64 
# # /opt/FlameGraph/stackcollapse-perf.pl perf.unfold &> perf.folded
# # /opt/FlameGraph/flamegraph.pl perf.folded > perf.svg

# /opt/FlameGraph/stackcollapse-stap.pl ${name}.bt >${name}.cbt
# /opt/FlameGraph/flamegraph.pl ${name}.cbt >${name}.svg
# rm -f temp.bt ${name}.bt ${name}.cbt

