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

if [ ! -d ${SERVER_ROOT}/libzip ];then

    cd $SOURCE_ROOT
    if [ ! -f ${SOURCE_ROOT}/libzip-1.3.2.tar.gz ];then
        wget -O libzip-1.3.2.tar.gz --no-check-certificate https://nih.at/libzip/libzip-1.3.2.tar.gz -T 20
    fi

    tar -zxvf libzip-1.3.2.tar.gz
    cd libzip-1.3.2

    ./configure --prefix=${SERVER_ROOT}/libzip && make && make install

    #cd $SOURCE_ROOT
    #rm -rf libzip-1.3.2
    #rm -rf libzip-1.3.2.tar.gz
fi