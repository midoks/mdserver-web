#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=7.0.9
SYS_ARCH=`arch`
SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
SYS_NAME=${SYS_VERSION_ID/./}

if [ "$SYS_NAME" -gt "11" ];then
	SYS_NAME="11"
fi

if [ "$SYS_NAME" -lt "11" ];then
	SYS_NAME="11"
fi

FILE_NAME=mongodb-linux-${SYS_ARCH}-debian${SYS_NAME}-${VERSION}
FILE_NAME_TGZ=${FILE_NAME}.tgz


MG_DIR=$serverPath/source/mongodb
mkdir -p $MG_DIR

if [ ! -f $MG_DIR/${FILE_NAME_TGZ} ]; then
	wget --no-check-certificate -O $MG_DIR/${FILE_NAME_TGZ} https://fastdl.mongodb.org/linux/${FILE_NAME_TGZ}
	echo "wget --no-check-certificate -O $MG_DIR/${FILE_NAME_TGZ} https://fastdl.mongodb.org/linux/${FILE_NAME_TGZ}"
fi

if [ ! -d $MG_DIR/${FILE_NAME_TGZ} ];then 
	cd $MG_DIR && tar -zxvf ${FILE_NAME_TGZ}
fi

if [ ! -d  $serverPath/mongodb/bin ];then
	mkdir -p $serverPath/mongodb
	cd $MG_DIR/${FILE_NAME} && cp -rf ./bin $serverPath/mongodb
fi

cd ${MG_DIR} && rm -rf ${MG_DIR}/${FILE_NAME}


TOOL_VERSION=2.2.5
TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-linux-x64
if [ "aarch64" == ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-linux-arm64
fi
TOOL_FILE_NAME_TGZ=${FILE_NAME}.tgz
if [ ! -f $MG_DIR/${TOOL_FILE_NAME_TGZ} ]; then
	wget --no-check-certificate -O $MG_DIR/mongosh-${TOOL_VERSION}-linux-x64.tgz https://downloads.mongodb.com/compass/mongosh-${TOOL_VERSION}-linux-x64.tgz
	echo "wget --no-check-certificate -O $MG_DIR/mongosh-${TOOL_VERSION}-linux-x64.tgz https://downloads.mongodb.com/compass/mongosh-${TOOL_VERSION}-linux-x64.tgz"
fi

if [ ! -d $MG_DIR/${TOOL_FILE_NAME_TGZ} ];then 
	cd $MG_DIR && tar -zxvf ${TOOL_FILE_NAME_TGZ}
fi

