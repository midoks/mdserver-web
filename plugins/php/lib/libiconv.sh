#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/php/lib && bash libiconv.sh

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

if [ ! -d ${SERVER_ROOT}/libiconv ];then
    cd $SOURCE_ROOT

    if [ "$LOCAL_ADDR" == 'cn' ];then
        if [ ! -f ${SOURCE_ROOT}/libiconv-1.15.tar.gz  ];then
            wget --no-check-certificate -O ${SOURCE_ROOT}/libiconv-1.15.tar.gz  https://dl.midoks.icu/lib/libiconv-1.15.tar.gz -T 20
        fi 
    fi

    if [ ! -f ${SOURCE_ROOT}/libiconv-1.15.tar.gz ];then
	   wget --no-check-certificate -O ${SOURCE_ROOT}/libiconv-1.15.tar.gz https://github.com/midoks/mdserver-web/releases/download/init/libiconv-1.15.tar.gz  -T 5
    fi

    if [ ! -d ${SOURCE_ROOT}/libiconv-1.15 ];then
        cd $SOURCE_ROOT && tar -zxvf libiconv-1.15.tar.gz
    fi

    cd ${SOURCE_ROOT}/libiconv-1.15

    ./configure --prefix=${SERVER_ROOT}/libiconv --enable-static && make && make install

    if [ -d $SOURCE_ROOT/libiconv-1.15 ];then 
        cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/libiconv-1.15
    fi
fi