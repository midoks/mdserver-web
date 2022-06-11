#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

echo $rootPath


SERVER_ROOT=/www/server/lib
SOURCE_ROOT=/www/server/source/lib

if [ ! -d ${SERVER_ROOT}/icu/52.2 ];then

	if [ ! -f ${SERVER_ROOT}/icu4c-52_2-src.tgz ];then
		wget -O ${SERVER_ROOT}/icu4c-52_2-src.tgz https://github.com/unicode-org/icu/releases/download/release-52-2/icu4c-52_2-src.tgz
	fi

	if [ ! -d ${SERVER_ROOT}/icu/52.2 ];then
		cd ${SERVER_ROOT} && tar -zxvf icu4c-52_2-src.tgz

		cd $MDIR/source/cmd/icu/source
		./runConfigureICU MacOSX  && make  CXXFLAGS="-g -O2 -std=c++11" && make install
	fi	

fi