#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=4.4.23
SYS_ARCH=`arch`

SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
SYS_NAME=${SYS_VERSION_ID/./}
# https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2004-4.4.23.tgz

if [ "$SYS_NAME" -gt "2004" ];then
	SYS_NAME="2004"
fi

if [ "$SYS_NAME" -lt "1604" ];then
	SYS_NAME="1604"
fi

MG_DIR=$serverPath/source/mongodb
mkdir -p $MG_DIR

FILE_NAME=mongodb-linux-${SYS_ARCH}-ubuntu${SYS_NAME}-${VERSION}
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

cd ${MG_DIR} && rm -rf ${MG_DIR}/${FILE_NAME}

#--------------- mongosh tool install ------------------ #
TOOL_VERSION=2.2.5
TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-linux-x64
if [ "aarch64" == ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-linux-arm64
fi
TOOL_FILE_NAME_TGZ=${TOOL_FILE_NAME}.tgz
if [ ! -f $MG_DIR/${TOOL_FILE_NAME_TGZ} ]; then
	wget --no-check-certificate -O $MG_DIR/${TOOL_FILE_NAME_TGZ} https://downloads.mongodb.com/compass/${TOOL_FILE_NAME_TGZ}
	echo "wget --no-check-certificate -O $MG_DIR/${TOOL_FILE_NAME_TGZ} https://downloads.mongodb.com/compass/${TOOL_FILE_NAME_TGZ}"
fi

if [ ! -d $MG_DIR/${TOOL_FILE_NAME_TGZ} ];then 
	cd $MG_DIR && tar -zxvf ${TOOL_FILE_NAME_TGZ}
fi

cd ${MG_DIR}/${TOOL_FILE_NAME} && cp -rf ./bin $serverPath/mongodb
cd ${MG_DIR} && rm -rf ${MG_DIR}/${TOOL_FILE_NAME}

# https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2204-x86_64-100.9.4.tgz
#--------------- mongodb database install ------------------ #
TOOL_VERSION=100.9.4
TOOL_FILE_NAME=mongodb-database-tools-ubuntu${SYS_NAME}-x86_64-${TOOL_VERSION}
if [ "aarch64" == ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongodb-database-tools-ubuntu${SYS_NAME}-arm64-${TOOL_VERSION}
fi

if [ "arm64" == ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongodb-database-tools-ubuntu${SYS_NAME}-arm64-${TOOL_VERSION}
fi

TOOL_FILE_NAME_TGZ=${TOOL_FILE_NAME}.tgz
if [ ! -f $MG_DIR/${TOOL_FILE_NAME_TGZ} ]; then
	wget --no-check-certificate -O $MG_DIR/${TOOL_FILE_NAME_TGZ} https://fastdl.mongodb.org/tools/db/${TOOL_FILE_NAME_TGZ}
fi

if [ ! -d $MG_DIR/${TOOL_FILE_NAME_TGZ} ];then 
	cd $MG_DIR && tar -zxvf ${TOOL_FILE_NAME_TGZ}
fi

cd ${MG_DIR}/${TOOL_FILE_NAME} && cp -rf ./bin $serverPath/mongodb
cd ${MG_DIR} && rm -rf ${MG_DIR}/${TOOL_FILE_NAME}