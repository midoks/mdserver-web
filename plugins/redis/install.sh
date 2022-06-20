#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=$2

Install_redis()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	if [ ! -f $serverPath/source/redis-${VERSION}.tar.gz ];then
		wget -O $serverPath/source/redis-${VERSION}.tar.gz http://download.redis.io/releases/redis-${VERSION}.tar.gz
	fi
	
	cd $serverPath/source && tar -zxvf redis-${VERSION}.tar.gz

	mkdir -p $serverPath/redis
	mkdir -p $serverPath/redis/data
	cd redis-${VERSION} && make PREFIX=$serverPath/redis install
	sed '/^ *#/d' redis.conf > $serverPath/redis/redis.conf

	echo "${VERSION}" > $serverPath/redis/version.pl

	echo '安装完成' > $install_tmp
}

Uninstall_redis()
{
	rm -rf $serverPath/redis

	if [ -f /lib/systemd/system/redis.service ];then
		rm -rf /lib/systemd/system/redis.service
	fi
	echo "Uninstall_redis" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_redis
else
	Uninstall_redis
fi
