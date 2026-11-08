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

VERSION=5.0.30

MG_DIR=$serverPath/source/mongodb
mkdir -p $MG_DIR

download "https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-${VERSION}.tgz" "$MG_DIR/mongodb-macos-x86_64-${VERSION}.tgz"

if [ ! -d $MG_DIR/mongodb-macos-x86_64-${VERSION} ];then 
	cd $MG_DIR && tar -zxvf mongodb-macos-x86_64-${VERSION}.tgz
fi

if [ ! -f $serverPath/mongodb/bin/mongod ];then
	mkdir -p $serverPath/mongodb
	cd $MG_DIR/mongodb-macos-x86_64-${VERSION} && cp -rf ./bin $serverPath/mongodb
fi

#--------------- mongosh tool install ------------------ #
TOOL_VERSION=2.2.5
TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-darwin-x64
if [ "aarch64" = ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-darwin-arm64
fi

if [ "arm64" = ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongosh-${TOOL_VERSION}-darwin-arm64
fi
TOOL_FILE_NAME_TGZ=${TOOL_FILE_NAME}.zip
download "https://downloads.mongodb.com/compass/${TOOL_FILE_NAME_TGZ}" "$MG_DIR/${TOOL_FILE_NAME_TGZ}"

if [ ! -d $MG_DIR/${TOOL_FILE_NAME_TGZ} ];then 
	cd $MG_DIR && unzip ${TOOL_FILE_NAME_TGZ}
fi

cd ${MG_DIR}/${TOOL_FILE_NAME} && cp -rf ./bin $serverPath/mongodb
cd ${MG_DIR} && rm -rf ${MG_DIR}/${TOOL_FILE_NAME}

#--------------- mongodb-database-tools ------------------ #
# https://fastdl.mongodb.org/tools/db/mongodb-database-tools-macos-arm64-100.9.4.zip
TOOL_VERSION=100.9.4
TOOL_FILE_NAME=mongodb-database-tools-macos-x86_64-${TOOL_VERSION}
if [ "aarch64" = ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongodb-database-tools-macos-arm64-${TOOL_VERSION}
fi

if [ "arm64" = ${SYS_ARCH} ];then
	TOOL_FILE_NAME=mongodb-database-tools-macos-arm64-${TOOL_VERSION}
fi

TOOL_FILE_NAME_TGZ=${TOOL_FILE_NAME}.zip
download "https://fastdl.mongodb.org/tools/db/${TOOL_FILE_NAME_TGZ}" "$MG_DIR/${TOOL_FILE_NAME_TGZ}"

if [ ! -d $MG_DIR/${TOOL_FILE_NAME_TGZ} ];then 
	cd $MG_DIR && unzip ${TOOL_FILE_NAME_TGZ}
fi

cd ${MG_DIR}/${TOOL_FILE_NAME} && cp -rf ./bin $serverPath/mongodb
cd ${MG_DIR} && rm -rf ${MG_DIR}/${TOOL_FILE_NAME}