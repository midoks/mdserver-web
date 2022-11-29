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

which rpcgen
if [ "$?" != "0" ];then
	
	if [ ! -f ${SOURCE_ROOT}/rpcsvc-proto-1.4.tar.gz ];then
		wget  --no-check-certificate -O ${SOURCE_ROOT}/rpcsvc-proto-1.4.tar.gz  https://github.com/thkukuk/rpcsvc-proto/releases/download/v1.4/rpcsvc-proto-1.4.tar.gz
	fi

	if [ ! -d ${SERVER_ROOT}/rpcsvc-proto-1.4 ];then
		cd ${SOURCE_ROOT} && tar -zxvf rpcsvc-proto-1.4.tar.gz
		cd ${SOURCE_ROOT}/rpcsvc-proto-1.4
		./configure && make  && make install
	fi	

fi