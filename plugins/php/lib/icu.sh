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

if [ ! -d ${SERVER_ROOT}/icu ];then

	if [ ! -f ${SOURCE_ROOT}/icu4c-52_2-src.tgz ];then
		wget -O ${SOURCE_ROOT}/icu4c-52_2-src.tgz https://github.com/unicode-org/icu/releases/download/release-52-2/icu4c-52_2-src.tgz
	fi

	if [ ! -d ${SERVER_ROOT}/icu/52.2 ];then
		cd ${SOURCE_ROOT} && tar -zxvf icu4c-52_2-src.tgz

		cd ${SOURCE_ROOT}/icu/source
		./runConfigureICU Linux --prefix=${SERVER_ROOT}/icu && make  CXXFLAGS="-g -O2 -std=c++11" && make install
	fi	

fi