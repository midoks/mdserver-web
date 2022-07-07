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
	wget -O libiconv-1.15.tar.gz  https://github.com/midoks/mdserver-web/releases/download/init/libiconv-1.15.tar.gz  -T 5
    tar zxvf libiconv-1.15.tar.gz
    cd libiconv-1.15
    ./configure --prefix=${SERVER_ROOT}/libiconv --enable-static && make && make install
    cd $SOURCE_ROOT
    #rm -rf libiconv-1.15
    #rm -rf libiconv-1.15.tar.gz
fi