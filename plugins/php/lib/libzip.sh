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


# cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
# HTTP_PREFIX="https://"
# if [ ! -z "$cn" ];then
#     HTTP_PREFIX="https://ghproxy.com/"
# fi

if [ ! -d ${SERVER_ROOT}/libzip ];then

    cd $SOURCE_ROOT
    if [ ! -f ${SOURCE_ROOT}/libzip-1.3.2.tar.gz ];then
        wget --no-check-certificate -O libzip-1.3.2.tar.gz --no-check-certificate https://libzip.org/download/libzip-1.3.2.tar.gz -T 20
    fi

    tar -zxvf libzip-1.3.2.tar.gz
    cd libzip-1.3.2

    ./configure --prefix=${SERVER_ROOT}/libzip && make && make install
    #cd $SOURCE_ROOT
    #rm -rf libzip-1.3.2
    #rm -rf libzip-1.3.2.tar.gz

    # cd $SOURCE_ROOT
    # if [ ! -f ${SOURCE_ROOT}/libzip-1.6.1.tar.gz ];then
    #     wget --no-check-certificate -O libzip-1.6.1.tar.gz ${HTTP_PREFIX}github.com/nih-at/libzip/releases/download/rel-1-6-1/libzip-1.6.1.tar.gz -T 20
    # fi

    # tar -zxvf libzip-1.6.1.tar.gz
    # cd ${SOURCE_ROOT}/libzip-1.6.1

    # cmake -DCMAKE_INSTALL_PREFIX=${SERVER_ROOT}/libzip && make && make install

fi