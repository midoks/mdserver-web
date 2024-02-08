#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

# echo $rootPath

SERVER_ROOT=$rootPath/lib
SOURCE_ROOT=$rootPath/source/lib

mkdir -p  $SOURCE_ROOT

HTTP_PREFIX="https://"
LOCAL_ADDR=common
cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
    LOCAL_ADDR=cn
    HTTP_PREFIX="https://mirror.ghproxy.com/"
fi
# HTTP_PREFIX="https://"

if [ ! -d ${SERVER_ROOT}/libzip ];then

    cd $SOURCE_ROOT

    if [ "$LOCAL_ADDR" == 'cn' ];then
        if [ ! -f ${SOURCE_ROOT}/libzip-1.3.2.tar.gz ];then
            wget --no-check-certificate -O libzip-1.3.2.tar.gz https://dl.midoks.icu/lib/libzip-1.3.2.tar.gz -T 20
        fi 
    fi

    # if [ ! -f ${SOURCE_ROOT}/libzip-1.3.2.tar.gz ];then
    #     wget --no-check-certificate -O libzip-1.3.2.tar.gz ${HTTP_PREFIX}github.com/midoks/mdserver-web/releases/download/init/libzip-1.3.2.tar.gz -T 20
    # fi

    if [ ! -f ${SOURCE_ROOT}/libzip-1.3.2.tar.gz ];then
        wget --no-check-certificate -O libzip-1.3.2.tar.gz https://github.com/midoks/mdserver-web/releases/download/init/libzip-1.3.2.tar.gz -T 20
    fi

    if [ ! -d ${SOURCE_ROOT}/libzip-1.3.2 ];then
        cd $SOURCE_ROOT && tar -zxvf libzip-1.3.2.tar.gz
    fi

    cd ${SOURCE_ROOT}/libzip-1.3.2

    ./configure --prefix=${SERVER_ROOT}/libzip && make && make install
    #cd $SOURCE_ROOT

    if [ "$?" == "0" ];then
        rm -rf ${SOURCE_ROOT}/libzip-1.3.2
        rm -rf ${SOURCE_ROOT}/libzip-1.3.2.tar.gz
    fi

fi