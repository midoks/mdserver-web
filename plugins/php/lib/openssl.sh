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

if [ ! -d ${SERVER_ROOT}/openssl ];then
    cd ${SOURCE_ROOT}
    if [ ! -f ${SOURCE_ROOT}/openssl-1.1.1p.tar.gz ];then
        wget -O ${SOURCE_ROOT}/openssl-1.1.1p.tar.gz https://www.openssl.org/source/openssl-1.1.1p.tar.gz
    fi 
    tar -zxvf openssl-1.1.1p.tar.gz
    cd openssl-1.1.1p
    ./config --prefix=${SERVER_ROOT}/openssl zlib-dynamic shared
    make && make install
fi

