#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
opensslVersion="1.1.1p"
# echo $rootPath

SERVER_ROOT=$rootPath/lib
SOURCE_ROOT=$rootPath/source/lib
mkdir -p $SOURCE_ROOT

if [ ! -d ${SERVER_ROOT}/openssl11 ];then
    cd ${SOURCE_ROOT}
    if [ ! -f ${SOURCE_ROOT}/openssl-${opensslVersion}.tar.gz ];then
        wget --no-check-certificate -O ${SOURCE_ROOT}/openssl-${opensslVersion}.tar.gz https://www.openssl.org/source/openssl-${opensslVersion}.tar.gz
    fi 
    tar -zxvf openssl-${opensslVersion}.tar.gz
    cd openssl-${opensslVersion}
    ./config --prefix=${SERVER_ROOT}/openssl11 zlib-dynamic shared
    make && make install

    # export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/www/server/lib/openssl11/lib
    if [ -d /etc/ld.so.conf.d ];then
        echo "/www/server/lib/openssl11/lib" > /etc/ld.so.conf.d/openssl11.conf
    elif [ -f /etc/ld.so.conf ]; then
        echo "/www/server/lib/openssl11/lib" >> /etc/ld.so.conf
    fi

    ldconfig
    # ldconfig -p  | grep openssl

    cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/openssl-${opensslVersion}
fi

