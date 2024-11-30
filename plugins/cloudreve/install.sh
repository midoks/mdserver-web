#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/cloudreve && bash install.sh install 3.8.3
# cd /www/server/mdserver-web/plugins/cloudreve && bash install.sh install 3.8.3

VERSION=$2

sysArch=`arch`
sysName=`uname`

ALIST_ARCH_NAME=amd64
if [ "$sysArch" == "arm64" ];then
	ALIST_ARCH_NAME=arm64
elif [ "$sysArch" == "x86_64" ]; then
	ALIST_ARCH_NAME=amd64
elif [ "$sysArch" == "aarch64" ]; then
	ALIST_ARCH_NAME=aarch64
fi

ALIST_NAME=linux
if [ "$sysName" == "Darwin" ];then
	ALIST_NAME=darwin
fi

Install_App()
{
	echo '正在安装脚本文件...'

	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/cloudreve

	FILE_TGZ=cloudreve_${VERSION}_${ALIST_NAME}_${ALIST_ARCH_NAME}.tar.gz
	CLOUDREVE_DIR=$serverPath/source/cloudreve

	if [ ! -f $CLOUDREVE_DIR/${FILE_TGZ} ];then
		wget -O $CLOUDREVE_DIR/${FILE_TGZ} https://github.com/cloudreve/Cloudreve/releases/download/${VERSION}/${FILE_TGZ}
	fi
	
	mkdir -p $serverPath/cloudreve

	cd $CLOUDREVE_DIR && tar -zxvf ${FILE_TGZ}  -C $serverPath/cloudreve
	echo "${VERSION}" > $serverPath/cloudreve/version.pl

	cd ${rootPath} && python3 ${rootPath}/plugins/cloudreve/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/cloudreve/index.py initd_install

	# cd $serverPath/cloudreve && ./alist admin set admin
	echo '安装cloudreve完成'
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/cloudreve.service ];then
		systemctl stop cloudreve
		systemctl disable cloudreve
		rm -rf /usr/lib/systemd/system/cloudreve.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/cloudreve.service ];then
		systemctl stop cloudreve
		systemctl disable cloudreve
		rm -rf /lib/systemd/system/cloudreve.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/cloudreve/initd/cloudreve ];then
		$serverPath/cloudreve/initd/cloudreve stop
	fi

	if [ -d $serverPath/cloudreve ];then
		rm -rf $serverPath/cloudreve
	fi
	
	echo "卸载cloudreve成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
