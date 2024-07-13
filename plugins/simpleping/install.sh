#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

ARCH=`uname -m`
sysName=`uname`
VERSION=$2

# 开启可以PING
# sysctl -w net.ipv4.ping_group_range="0 2147483647"

install_tmp=${rootPath}/tmp/mw_install.pl

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/simpleping

	name=linux
	if [ "$sysName" == "Darwin" ];then
		name="darwin"
	else
		sysctl -w net.ipv4.ping_group_range="0 2147483647"
	fi

	if [ "$ARCH" == "x86_64" ];then
		ARCH="amd64"
	fi

	FILE_TGZ=simpleping_${name}_${ARCH}.tar.gz
	APP_DIR=$serverPath/source/simpleping

	# https://github.com/midoks/simpleping/releases/download/1.0/simpleping_linux_amd64.tar.gz
	if [ ! -f $APP_DIR/${FILE_TGZ} ];then
		wget -O $APP_DIR/${FILE_TGZ} https://github.com/midoks/simpleping/releases/download/2.0/${FILE_TGZ}
	fi
	
	mkdir -p $serverPath/simpleping
	cd $APP_DIR && tar -zxvf ${FILE_TGZ} -C $serverPath/simpleping
	echo "${VERSION}" > $serverPath/simpleping/version.pl

	cd ${rootPath} && python3 ${rootPath}/plugins/simpleping/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/simpleping/index.py initd_install

	echo '安装SimplePing成功!'

}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/simpleping.service ];then
		systemctl stop simpleping
		systemctl disable simpleping
		rm -rf /usr/lib/systemd/system/simpleping.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/simpleping.service ];then
		systemctl stop simpleping
		systemctl disable simpleping
		rm -rf /lib/systemd/system/simpleping.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/simpleping/initd/simpleping ];then
		$serverPath/simpleping/initd/simpleping stop
	fi

	if [ -d $serverPath/simpleping ];then
		rm -rf $serverPath/simpleping
	fi
	
	echo "卸载SimplePing成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
