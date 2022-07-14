#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

# echo $rootPath

SERVER_ROOT=$rootPath/lib
SOURCE_ROOT=$rootPath/source/lib

which onig-config
if [ "$?" != "0" ];then
    cd ${SOURCE_ROOT}
    if [ ! -f ${SOURCE_ROOT}/oniguruma-6.9.4.tar.gz ];then
        wget -O ${SOURCE_ROOT}/oniguruma-6.9.4.tar.gz https://github.com/kkos/oniguruma/archive/v6.9.4.tar.gz
    fi 
    cd ${SOURCE_ROOT} && tar -zxvf oniguruma-6.9.4.tar.gz
    cd ${SOURCE_ROOT}/oniguruma-6.9.4 && ./autogen.sh && ./configure --prefix=/usr && make && make install
fi

