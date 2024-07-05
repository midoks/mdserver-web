#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
SYS_ARCH=`arch`

# export GOPROXY=https://goproxy.io
# export GO111MODULE=on


apt -y install build-essential git make libelf-dev strace tar bpfcc-tools libbpf-dev

# clang -v
apt -y install clang llvm

apt -y install golang
