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

if [ ! -d ${SERVER_ROOT}/libiconv ];then

    cd $SOURCE_ROOT
    if [ ! -f ${SOURCE_ROOT}/zlib-1.2.11.tar.gz ];then
        wget -O zlib-1.2.11.tar.gz --no-check-certificate https://github.com/madler/zlib/archive/v1.2.11.tar.gz -T 20
    fi

    tar -zxvf zlib-1.2.11.tar.gz
    cd zlib-1.2.11

    ./configure --prefix=${SERVER_ROOT}/zlib && make && make install

    #cd $SOURCE_ROOT
    #rm -rf zlib-1.2.11
    #rm -rf zlib-1.2.11.tar.gz
fi