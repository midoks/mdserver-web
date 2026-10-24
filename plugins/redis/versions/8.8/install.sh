#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

action=$1

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=8.8.3
PLUGIN_VERSION=8.8

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/redis

	FILE_TGZ=redis-${VERSION}.tar.gz
	REDIS_DIR=$serverPath/source/redis

	if [ ! -f $REDIS_DIR/${FILE_TGZ} ];then
		wget --no-check-certificate -O $REDIS_DIR/${FILE_TGZ} https://download.redis.io/releases/${FILE_TGZ}
	fi
	
	cd $REDIS_DIR && tar -zxvf ${FILE_TGZ}

	CMD_MAKE=`which gmake`
	if [ "$?" = "0" ];then
		cd redis-${VERSION} && gmake PREFIX=$serverPath/redis install
	else
		cd redis-${VERSION} && make PREFIX=$serverPath/redis install
	fi

	if [ ! -d $serverPath/redis/data ];then
		mkdir -p $serverPath/redis/data
		sed '/^ *#/d' redis.conf > $serverPath/redis/redis.conf
		echo '安装完成'
	fi

	echo "${PLUGIN_VERSION}" > $serverPath/redis/version.pl

	if [ -d ${REDIS_DIR}/redis-${VERSION} ];then
		rm -rf ${REDIS_DIR}/redis-${VERSION}
	fi
}

Uninstall_App()
{
	echo "卸载redis成功"
}

if [ "${1}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_App
elif [ "${1}" = 'uninstall' ];then
	Uninstall_App
else
	echo "OPTIONS ERROR"
fi
