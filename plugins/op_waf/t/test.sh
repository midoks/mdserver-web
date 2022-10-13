#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# apt install apache2-utils
# yum -y install httpd-tools
# ab -c 1000 -n 1000000 http://www.zzzvps.com/
# /cc https://www.zzzvps.com/ 120
# ab -c 10 -n 1000 http://t1.cn/wp-admin/index.php
# ab -c 1000 -n 1000000 http://dev156.cachecha.com/

python3 index.py


# 安装 火焰图
# sudo apt install elfutils
# sudo apt-get build-dep systemtap
# systemtap
# stap -e 'probe kernel.function("sys_open") {log("hello world") exit()}'
# stap -v -e 'probe vfs.read {printf("read performed\n"); exit()}'


# yum -y kernel-devel kernel-headers gcc elfutils
# stap -ve 'probe begin { log("hello systemtap!") exit() }'
# stap -e 'probe vfs.add_to_page_cache {printf("dev=%d, devname=%s, ino=%d, index=%d, nrpages=%d\n", dev, devname, ino, index, nrpages )}'
# git clone https://github.com/openresty/openresty-systemtap-toolkit
# http://openresty.org/en/build-systemtap.html

# ./configure --prefix=/opt/stap --disable-docs --disable-publican --disable-refdocs CFLAGS="-g -O2"

# apt-get install systemtap linux-image-`uname -r`-dbg linux-headers-`uname -r`
# /usr/share/doc/systemtap/README.Debian
# ./ngx-active-reqs -p 383774


# wget -O kernel-debuginfo-$(uname -r).rpm http://debuginfo.centos.org/8/x86_64/kernel-debuginfo-$(uname -r).rpm

# wget -O kernel-debuginfo-4.18.0-348.el8.x86_64.rpm http://debuginfo.centos.org/8/x86_64/Packages/kernel-debuginfo-4.18.0-348.el8.x86_64.rpm
# wget -O kernel-debuginfo-common-x86_64-4.18.0-348.el8.x86_64.rpm http://debuginfo.centos.org/8/x86_64/Packages/kernel-debuginfo-common-x86_64-4.18.0-348.el8.x86_64.rpm

# rpm -ivh kernel-debuginfo-4.18.0-348.el8.x86_64.rpm
# rpm -ivh kernel-debuginfo-common-x86_64-4.18.0-348.el8.x86_64.rpm
# uname -r 

# yum install kernel-devel-4.18.0-358.el8.x86_64
# yum install kernel-debuginfo-4.18.0-358.el8.x86_64

# yum search kernel-debuginfo
# kernel-devel

# rpm -ivh kernel-debuginfo-4.18.0-358.el8.x86_64
# yum install systemtap -y
# yum install perf -y


# perf record -F 99  -p 4452 -g -o test.data -- sleep 100


# perf record -F 99  -p 153145 -g -o test.data -- sleep 100

# perf script -i test.data &> perf.unfold
# ./FlameGraph/stackcollapse-perf.pl perf.unfold &> perf.folded
# ./FlameGraph/flamegraph.pl perf.folded > perf.svg

#
# git clone https://github.com/brendangregg/FlameGraph.git

# git clone https://github.com/openresty/openresty-systemtap-toolkit
# ps -ef|grep openresty | grep -v grep | awk '{print $2}'
# ./ngx-active-reqs -p 153145





