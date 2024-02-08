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

HTTP_PREFIX="https://"
cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
    HTTP_PREFIX="https://mirror.ghproxy.com/"
fi

which onig-config
if [ "$?" != "0" ];then
    cd ${SOURCE_ROOT}
    if [ ! -f ${SOURCE_ROOT}/oniguruma-6.9.4.tar.gz ];then
        wget --no-check-certificate -O ${SOURCE_ROOT}/oniguruma-6.9.4.tar.gz ${HTTP_PREFIX}github.com/kkos/oniguruma/archive/v6.9.4.tar.gz
    fi

    if [ ! -d  cd ${SOURCE_ROOT}/oniguruma-6.9.4 ];then
        cd ${SOURCE_ROOT} && tar -zxvf oniguruma-6.9.4.tar.gz
    fi
    
    cd ${SOURCE_ROOT}/oniguruma-6.9.4 && ./autogen.sh && ./configure --prefix=/usr && make && make install
    cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/oniguruma-6.9.4
fi

