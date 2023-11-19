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

if [ ! -d ${SERVER_ROOT}/freetype ];then
    cd $SOURCE_ROOT

    if [ ! -f $SOURCE_ROOT/freetype-2.12.1.tar.gz ];then
	   wget -O freetype-2.12.1.tar.gz --no-check-certificate https://download.savannah.gnu.org/releases/freetype/freetype-2.12.1.tar.gz  -T 5
    fi

    if [ ! -d $SOURCE_ROOT/freetype-2.12.1 ];then
        tar zxvf freetype-2.12.1.tar.gz
        cd freetype-2.12.1
    else
        cd freetype-2.12.1
    fi

    ./configure --prefix=${SERVER_ROOT}/freetype && make && make install
    cd $SOURCE_ROOT && rm -rf freetype-2.12.1
    #rm -rf freetype-2.12.1.tar.gz
    cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/freetype-2.12.1
    
fi