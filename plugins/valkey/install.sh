#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# https://www.cnblogs.com/zlonger/p/16177595.html
# https://www.cnblogs.com/BNTang/articles/15841688.html

# ps -ef|grep valkey |grep -v grep | awk '{print $2}' | xargs kill

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/valkey && bash install.sh install 7.2.2

# cmd查看| info replication
# /Users/midoks/Desktop/mwdev/server/valkey/bin/valkey-cli -h 127.0.0.1 -p 6399
# /www/server/valkey/bin/valkey-cli -h 127.0.0.1 -p 6399

VERSION=$2

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/valkey

	FILE_TGZ=${VERSION}.tar.gz
	VALKEY_DIR=$serverPath/source/valkey

	if [ ! -f $VALKEY_DIR/${FILE_TGZ} ];then
		wget --no-check-certificate -O $VALKEY_DIR/${FILE_TGZ} https://github.com/valkey-io/valkey/archive/refs/tags/${FILE_TGZ}
	fi
	
	cd $VALKEY_DIR && tar -zxvf ${FILE_TGZ}

	CMD_MAKE=`which gmake`
	if [ "$?" == "0" ];then
		cd valkey-${VERSION} && gmake PREFIX=$serverPath/valkey install
	else
		cd valkey-${VERSION} && make PREFIX=$serverPath/valkey install
	fi

	if [ -d $serverPath/valkey ];then
		mkdir -p $serverPath/valkey/data
		sed '/^ *#/d' valkey.conf > $serverPath/valkey/valkey.conf

		echo "${VERSION}" > $serverPath/valkey/version.pl
		echo '安装完成'

		cd ${rootPath} && python3 plugins/valkey/index.py start
		cd ${rootPath} && python3 plugins/valkey/index.py initd_install
		
	else
		echo '安装失败!'
	fi

	if [ -d ${REDIS_DIR}/valkey-${VERSION} ];then
		rm -rf ${REDIS_DIR}/valkey-${VERSION}
	fi
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/valkey.service ];then
		systemctl stop valkey
		systemctl disable valkey
		rm -rf /usr/lib/systemd/system/valkey.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/valkey.service ];then
		systemctl stop valkey
		systemctl disable valkey
		rm -rf /lib/systemd/system/valkey.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/valkey/initd/valkey ];then
		$serverPath/valkey/initd/valkey stop
	fi

	if [ -d $serverPath/valkey ];then
		rm -rf $serverPath/valkey
	fi
	
	echo "卸载valkey成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
