#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

SERVER_ROOT=$rootPath/lib
SOURCE_ROOT=$rootPath/source/lib
mkdir -p $SOURCE_ROOT

pcreVersion='8.38'

if [ ! -d ${SERVER_ROOT}/pcre ];then
    cd ${SOURCE_ROOT}

    if [ ! -f ${SOURCE_ROOT}/pcre-${pcreVersion}.tar.gz ];then
        wget --no-check-certificate -O ${SOURCE_ROOT}/pcre-${pcreVersion}.tar.gz https://netix.dl.sourceforge.net/project/pcre/pcre/${pcreVersion}/pcre-${pcreVersion}.tar.gz
    fi
    

    if [ ! -d ${SOURCE_ROOT}/pcre-${pcreVersion} ];then
        cd ${SOURCE_ROOT} && tar -zxvf pcre-${pcreVersion}.tar.gz
        
    fi

    cd ${SOURCE_ROOT}/pcre-${pcreVersion}
    ./configure --prefix=${SERVER_ROOT}/pcre
    make && make install

    cd $SOURCE_ROOT && rm -rf ${SOURCE_ROOT}/pcre-${pcreVersion}
fi

