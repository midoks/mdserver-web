#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# 安全下载:先写入临时文件,成功后原子重命名,避免下载失败残留不完整文件导致重试被跳过
download() {
    local url="$1"
    local out="$2"
    if [ -f "$out" ]; then
        return 0
    fi
    local tmp="${out}.downloading"
    rm -f "$tmp"
    if command -v wget >/dev/null 2>&1; then
        wget --no-check-certificate -O "$tmp" "$url"
    else
        curl -fLk -o "$tmp" "$url"
    fi
    if [ $? -ne 0 ] || [ ! -s "$tmp" ]; then
        rm -f "$tmp"
        echo "download failed: $url"
        return 1
    fi
    mv -f "$tmp" "$out"
    echo "download $out successful!"
    return 0
}


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=4.4.23
SYS_ARCH=`arch`

SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
SYS_NAME=${SYS_VERSION_ID/./}
SYS_NAME_LEN=`echo "$SYS_NAME" | wc -L`

if [ "$SYS_NAME_LEN" = "1" ];then
	SYS_NAME=${SYS_NAME}0	
fi

if [ "$SYS_ARCH" = "aarch64" ];then
	if [ "$SYS_NAME" -gt "82" ];then
		SYS_NAME="82"
	fi

	if [ "$SYS_NAME" -lt "62" ];then
		SYS_NAME="62"
	fi
else

	if [ "$SYS_NAME" -gt "80" ];then
		SYS_NAME="80"
	fi

	if [ "$SYS_NAME" -lt "70" ];then
		SYS_NAME="70"
	fi
fi


# https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-rhel82-4.4.23.tgz
# https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel70-4.4.23.tgz
# https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel80-4.4.23.tgz
# https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-rhel82-4.4.23.tgz
# https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel80-4.4.23.tgz

MG_DIR=$serverPath/source/mongodb
mkdir -p $MG_DIR

FILE_NAME=mongodb-linux-${SYS_ARCH}-rhel${SYS_NAME}-${VERSION}
FILE_NAME_TGZ=${FILE_NAME}.tgz

download "https://fastdl.mongodb.org/linux/${FILE_NAME_TGZ}" "$MG_DIR/${FILE_NAME_TGZ}"

if [ ! -d $MG_DIR/${FILE_NAME} ];then 
	cd $MG_DIR && tar -zxvf ${FILE_NAME_TGZ}
fi

if [ ! -f $serverPath/mongodb/bin/mongod ];then
	mkdir -p $serverPath/mongodb
	cd $MG_DIR/${FILE_NAME} && cp -rf ./bin $serverPath/mongodb
fi

cd ${MG_DIR} && rm -rf ${MG_DIR}/${FILE_NAME}

#--------------- mongosh tool install ------------------ #
TOOL_VERSION=2.2.5
TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-linux-x64
if [ "aarch64" = ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-linux-arm64
fi
TOOL_FILE_NAME_TGZ=${TOOL_FILE_NAME}.tgz
download "https://downloads.mongodb.com/compass/${TOOL_FILE_NAME_TGZ}" "$MG_DIR/${TOOL_FILE_NAME_TGZ}"

if [ ! -d $MG_DIR/${TOOL_FILE_NAME_TGZ} ];then 
	cd $MG_DIR && tar -zxvf ${TOOL_FILE_NAME_TGZ}
fi

cd ${MG_DIR}/${TOOL_FILE_NAME} && cp -rf ./bin $serverPath/mongodb
cd ${MG_DIR} && rm -rf ${MG_DIR}/${TOOL_FILE_NAME}

#--------------- mongodb database install ------------------ #
TOOL_VERSION=100.9.4
TOOL_FILE_NAME=mongodb-database-tools-rhel${SYS_NAME}-x86_64-${TOOL_VERSION}
if [ "aarch64" = ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongodb-database-tools-rhel${SYS_NAME}-aarch64-${TOOL_VERSION}
fi

if [ "arm64" = ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongodb-database-tools-rhel${SYS_NAME}-arm64-${TOOL_VERSION}
fi

TOOL_FILE_NAME_TGZ=${TOOL_FILE_NAME}.tgz
download "https://fastdl.mongodb.org/tools/db/${TOOL_FILE_NAME_TGZ}" "$MG_DIR/${TOOL_FILE_NAME_TGZ}"

if [ ! -d $MG_DIR/${TOOL_FILE_NAME_TGZ} ];then 
	cd $MG_DIR && tar -zxvf ${TOOL_FILE_NAME_TGZ}
fi

cd ${MG_DIR}/${TOOL_FILE_NAME} && cp -rf ./bin $serverPath/mongodb
cd ${MG_DIR} && rm -rf ${MG_DIR}/${TOOL_FILE_NAME}
