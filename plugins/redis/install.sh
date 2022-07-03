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

	if [ -d $serverPath/redis ];then
		echo "${VERSION}" > $serverPath/redis/version.pl
		echo '安装完成' > $install_tmp


		cd ${rootPath} && python3 ${rootPath}/plugins/redis/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/redis/index.py initd_install
	fi
}

Uninstall_redis()
{
	if [ -f /usr/lib/systemd/system/redis.service ];then
		systemctl stop redis
		systemctl disable redis
		rm -rf /usr/lib/systemd/system/redis.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/redis/initd/redis ];then
		$serverPath/redis/initd/redis stop
	fi

	rm -rf $serverPath/redis
	echo "Uninstall_redis" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_redis
else
	Uninstall_redis
fi
