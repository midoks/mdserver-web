#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/php/lib && bash libedit.sh

# echo $rootPath

SERVER_ROOT=$rootPath/lib
SOURCE_ROOT=$rootPath/source/lib


# LOCAL_ADDR=common
# cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
# if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
#     LOCAL_ADDR=cn
# fi

if [ ! -d ${SERVER_ROOT}/libedit ];then
    cd $SOURCE_ROOT

    VERSION="20230828-3.1"

    if [ ! -f ${SOURCE_ROOT}/libedit-${VERSION}.tar.gz ];then
	   wget --no-check-certificate -O ${SOURCE_ROOT}/libedit-${VERSION}.tar.gz https://thrysoee.dk/editline/libedit-${VERSION}.tar.gz
    fi

    if [ ! -d ${SOURCE_ROOT}/libedit-${VERSION} ];then
        cd $SOURCE_ROOT && tar -zxvf libedit-${VERSION}.tar.gz
    fi

    cd ${SOURCE_ROOT}/libedit-${VERSION}

    ./configure --prefix=${SERVER_ROOT}/libedit && make && make install

    if [ -d $SOURCE_ROOT/libedit-${VERSION} ];then 
        cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/libedit-${VERSION}
    fi
fi