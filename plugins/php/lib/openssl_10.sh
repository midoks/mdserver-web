#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

opensslVersion="1.0.2q"
# echo $rootPath

SERVER_ROOT=$rootPath/lib
SOURCE_ROOT=$rootPath/source/lib

HTTP_PREFIX="https://"
LOCAL_ADDR=common
cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
    LOCAL_ADDR=cn
    HTTP_PREFIX="https://mirror.ghproxy.com/"
fi

if [ ! -d ${SERVER_ROOT}/openssl10 ];then
    cd ${SOURCE_ROOT}

    if [ "$LOCAL_ADDR" == 'cn' ];then
        if [ ! -f ${SOURCE_ROOT}/openssl-${opensslVersion}.tar.gz ];then
            wget --no-check-certificate -O openssl-${opensslVersion}.tar.gz https://dl.midoks.icu/lib/openssl-${opensslVersion}.tar.gz -T 20
        fi 
    fi

    # if [ ! -f ${SOURCE_ROOT}/openssl-${opensslVersion}.tar.gz ];then
    #     wget --no-check-certificate ${HTTP_PREFIX}/midoks/mdserver-web/releases/download/init/openssl-${opensslVersion}.tar.gz -T 20
    # fi

    if [ ! -f ${SOURCE_ROOT}/openssl-${opensslVersion}.tar.gz ];then
        wget --no-check-certificate -O openssl-${opensslVersion}.tar.gz https://github.com/midoks/mdserver-web/releases/download/init/openssl-${opensslVersion}.tar.gz -T 20
    fi

    tar -zxf openssl-${opensslVersion}.tar.gz
    cd openssl-${opensslVersion}
    ./config --openssldir=${SERVER_ROOT}/openssl10 zlib-dynamic shared
    make && make install

    cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/openssl-${opensslVersion}
fi


