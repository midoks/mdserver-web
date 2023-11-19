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


VERSION=1.0.18
#----------------------------- libsodium start -------------------------#
if [ ! -f /usr/local/lib/libsodium.so ];then
    cd ${SOURCE_ROOT}
    if [ ! -f ${SOURCE_ROOT}/libsodium-${VERSION}-stable.tar.gz ];then
        # wget --no-check-certificate -O libsodium-1.0.18-stable.tar.gz https://download.libsodium.org/libsodium/releases/libsodium-1.0.18-stable.tar.gz -T 20
        wget --no-check-certificate -O libsodium-${VERSION}-stable.tar.gz https://download.libsodium.org/libsodium/releases/libsodium-${VERSION}-stable.tar.gz -T 20
    fi 
    tar -zxvf libsodium-${VERSION}-stable.tar.gz
    cd libsodium-stable
    ./configure  && make && make check && make install

    cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/libsodium-stable
fi
#----------------------------- libsodium end -------------------------#