#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

actionType=$1
version=$2

sysName=`uname`
LIBNAME=opcache

cfgDir=/etc/opt/remi

if [ "$actionType" == 'install' ];then
	apt install -y php${version}-${LIBNAME}
	echo "ls ${cfgDir}/php${version}/php.d | grep "${LIBNAME}""
	find_opcache=`ls ${cfgDir}/php${version}/php.d | grep "${LIBNAME}"`
	echo $find_opcache
elif [ "$actionType" == 'uninstall' ];then
	echo 'cannot uninstall'
	exit 1
fi