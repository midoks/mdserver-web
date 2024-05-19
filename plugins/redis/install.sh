#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# https://www.cnblogs.com/zlonger/p/16177595.html
# https://www.cnblogs.com/BNTang/articles/15841688.html

# ps -ef|grep redis |grep -v grep | awk '{print $2}' | xargs kill

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/redis && bash install.sh install 7.2.2

# cmd查看| info replication
# /Users/midoks/Desktop/mwdev/server/redis/bin/redis-cli -h 127.0.0.1 -p 6399
# /www/server/redis/bin/redis-cli -h 127.0.0.1 -p 6399

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/redis

	FILE_TGZ=redis-${VERSION}.tar.gz
	REDIS_DIR=$serverPath/source/redis

	if [ ! -f $REDIS_DIR/${FILE_TGZ} ];then
		wget -O $REDIS_DIR/${FILE_TGZ} http://download.redis.io/releases/${FILE_TGZ}
	fi
	
	cd $REDIS_DIR && tar -zxvf ${FILE_TGZ}

	CMD_MAKE=`which gmake`
	if [ "$?" == "0" ];then
		cd redis-${VERSION} && gmake PREFIX=$serverPath/redis install
	else
		cd redis-${VERSION} && make PREFIX=$serverPath/redis install
	fi

	if [ -d $serverPath/redis ];then
		mkdir -p $serverPath/redis/data
		sed '/^ *#/d' redis.conf > $serverPath/redis/redis.conf

		echo "${VERSION}" > $serverPath/redis/version.pl
		echo '安装完成'

		cd ${rootPath} && python3 ${rootPath}/plugins/redis/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/redis/index.py initd_install
		
	else
		echo '安装失败!'
	fi

	if [ -d ${REDIS_DIR}/redis-${VERSION} ];then
		rm -rf ${REDIS_DIR}/redis-${VERSION}
	fi
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/redis.service ];then
		systemctl stop redis
		systemctl disable redis
		rm -rf /usr/lib/systemd/system/redis.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/redis.service ];then
		systemctl stop redis
		systemctl disable redis
		rm -rf /lib/systemd/system/redis.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/redis/initd/redis ];then
		$serverPath/redis/initd/redis stop
	fi

	if [ -d $serverPath/redis ];then
		rm -rf $serverPath/redis
	fi
	
	echo "卸载redis成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
