#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=6.0.9

MG_DIR=$serverPath/source/mongodb
mkdir -p $MG_DIR

if [ ! -f $MG_DIR/mongodb-linux-x86_64-debian11-${VERSION}.tgz ]; then
	wget --no-check-certificate -O $MG_DIR/mongodb-linux-x86_64-debian11-${VERSION}.tgz https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian11-${VERSION}.tgz
	echo "wget --no-check-certificate -O mongodb-linux-x86_64-debian11-${VERSION}.tgz https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian11-${VERSION}.tgz"
fi

if [ ! -d $MG_DIR/mongodb-linux-x86_64-debian11-${VERSION} ];then 
	cd $MG_DIR && tar -zxvf mongodb-linux-x86_64-debian11-${VERSION}.tgz
fi

if [ ! -d  $serverPath/mongodb/bin ];then
	mkdir -p $serverPath/mongodb
	cd $MG_DIR/mongodb-linux-x86_64-debian11-${VERSION} && cp -rf ./bin $serverPath/mongodb
fi