#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl


Install_redis()
{

	echo '正在安装脚本文件...' > $install_tmp

	wget -O $serverPath/source/redis.tar.gz http://download.redis.io/releases/redis-4.0.11.tar.gz
	cd $serverPath/source && tar -zxvf redis.tar.gz

	mkdir -p $serverPath/redis
	cd redis* && make PREFIX=$serverPath/redis install
	sed '/^ *#/d' redis.conf > $serverPath/redis/redis.conf

	echo '4.0' > $serverPath/redis/version.pl

	echo '安装完成' > $install_tmp
}

Uninstall_redis()
{
	rm -rf $serverPath/redis
	echo "Uninstall_redis" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_redis
else
	Uninstall_redis
fi
