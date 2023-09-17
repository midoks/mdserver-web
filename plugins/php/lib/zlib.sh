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

HTTP_PREFIX="https://"
cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
    HTTP_PREFIX="https://ghproxy.com/"
fi

if [ ! -d ${SERVER_ROOT}/zlib ];then

    cd $SOURCE_ROOT
    if [ ! -f ${SOURCE_ROOT}/zlib-1.2.11.tar.gz ];then
        wget --no-check-certificate -O zlib-1.2.11.tar.gz ${HTTP_PREFIX}github.com/madler/zlib/archive/v1.2.11.tar.gz -T 20
    fi

    tar -zxvf zlib-1.2.11.tar.gz
    cd zlib-1.2.11

    ./configure --prefix=${SERVER_ROOT}/zlib && make && make install

    #cd $SOURCE_ROOT
    #rm -rf zlib-1.2.11
    #rm -rf zlib-1.2.11.tar.gz
fi