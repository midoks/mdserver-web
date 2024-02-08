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
LOCAL_ADDR=common
cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
    LOCAL_ADDR=cn
    HTTP_PREFIX="https://mirror.ghproxy.com/"
fi

if [ ! -d ${SERVER_ROOT}/icu ];then
	
	cd ${SOURCE_ROOT}

	if [ "$LOCAL_ADDR" == 'cn' ];then
        if [ ! -f ${SOURCE_ROOT}/icu4c-52_2-src.tgz  ];then
            wget --no-check-certificate -O ${SOURCE_ROOT}/icu4c-52_2-src.tgz https://dl.midoks.icu/lib/icu4c-52_2-src.tgz -T 20
        fi 
    fi

	if [ ! -f ${SOURCE_ROOT}/icu4c-52_2-src.tgz ];then
		wget --no-check-certificate -O ${SOURCE_ROOT}/icu4c-52_2-src.tgz https://github.com/unicode-org/icu/releases/download/release-52-2/icu4c-52_2-src.tgz
	fi

	if [ ! -d ${SERVER_ROOT}/lib/icu/lib ];then
		cd ${SOURCE_ROOT} && tar -zxvf icu4c-52_2-src.tgz

		cd ${SOURCE_ROOT}/icu/source
		./runConfigureICU Linux --prefix=${SERVER_ROOT}/icu && make  CXXFLAGS="-g -O2 -std=c++11" && make install

		# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/www/server/lib/icu/lib
		if [ -d /etc/ld.so.conf.d ];then
			echo "/www/server/lib/icu/lib" > /etc/ld.so.conf.d/mw-icu.conf
		elif [[ -f /etc/ld.so.conf ]]; then
			echo "/www/server/lib/icu/lib" >> /etc/ld.so.conf
		fi

		ldconfig

		cd $SOURCE_ROOT && rm -rf ${SOURCE_ROOT}/icu
	fi

fi