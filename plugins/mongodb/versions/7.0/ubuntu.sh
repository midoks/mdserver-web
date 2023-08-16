#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=7.0.0
SYS_ARCH=`arch`

OSNAME=`cat ${rootPath}/data/osname.pl`
SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

# https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-ubuntu2204-7.0.0.tgz

MG_DIR=$serverPath/source/mongodb
mkdir -p $MG_DIR

FILE_NAME=mongodb-linux-${SYS_ARCH}-ubuntu2204-${VERSION}
FILE_NAME_TGZ=${FILE_NAME}.tgz

if [ ! -f $MG_DIR/${FILE_NAME_TGZ} ]; then
	wget --no-check-certificate -O $MG_DIR/${FILE_NAME_TGZ} https://fastdl.mongodb.org/linux/${FILE_NAME_TGZ}
	echo "wget --no-check-certificate -O $MG_DIR/${FILE_NAME_TGZ} https://fastdl.mongodb.org/linux/${FILE_NAME_TGZ}"
fi

if [ ! -d $MG_DIR/${FILE_NAME} ];then 
	cd $MG_DIR && tar -zxvf ${FILE_NAME_TGZ}
fi

if [ ! -d  $serverPath/mongodb/bin ];then
	mkdir -p $serverPath/mongodb
	cd $MG_DIR/${FILE_NAME} && cp -rf ./bin $serverPath/mongodb
fi