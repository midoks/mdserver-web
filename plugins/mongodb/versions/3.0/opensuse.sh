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

VERSION=3.0.15
SYS_ARCH=`arch`

if [ "$SYS_ARCH" != "x86_64" ];then
	echo "no support"
	exit 0
fi

SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}' | awk -F . '{print $1}'`
SYS_BID=${SYS_VERSION_ID/./}
SYS_NAME="15"
if [ "$SYS_BID" -lt "12" ];then
	SYS_NAME="12"
fi


# https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-suse15-4.4.23.tgz
# https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-suse12-4.4.23.tgz

MG_DIR=$serverPath/source/mongodb
mkdir -p $MG_DIR

FILE_NAME=mongodb-linux-${SYS_ARCH}-${VERSION}
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
