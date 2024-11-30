#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/alist && bash install.sh install 3.37.4
# cd /www/server/mdserver-web/plugins/alist && bash install.sh install 3.37.4

VERSION=$2

sysArch=`arch`
sysName=`uname`

ALIST_ARCH_NAME=amd64
if [ "$sysArch" == "arm64" ];then
	ALIST_ARCH_NAME=arm64
elif [ "$sysArch" == "x86_64" ]; then
	ALIST_ARCH_NAME=amd64
elif [ "$sysArch" == "aarch64" ]; then
	ALIST_ARCH_NAME=arm64
fi

ALIST_NAME=linux
if [ "$sysName" == "Darwin" ];then
	ALIST_NAME=darwin
fi

Install_App()
{
	echo '正在安装脚本文件...'

	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/alist

	FILE_TGZ=alist-${ALIST_NAME}-${ALIST_ARCH_NAME}.tar.gz

	ALIST_DIR=$serverPath/source/alist

	if [ ! -f $ALIST_DIR/${FILE_TGZ} ];then
		wget -O $ALIST_DIR/${FILE_TGZ} https://github.com/alist-org/alist/releases/download/v${VERSION}/${FILE_TGZ}
	fi
	
	mkdir -p $serverPath/alist

	cd $ALIST_DIR && tar -zxvf ${FILE_TGZ}  -C $serverPath/alist
	echo "${VERSION}" > $serverPath/alist/version.pl

	cd ${rootPath} && python3 ${rootPath}/plugins/alist/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/alist/index.py initd_install

	cd $serverPath/alist && ./alist admin set admin
	# cd /www/server/alist && ./alist admin set admin

	echo '安装完成'
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/alist.service ];then
		systemctl stop alist
		systemctl disable alist
		rm -rf /usr/lib/systemd/system/alist.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/alist.service ];then
		systemctl stop alist
		systemctl disable alist
		rm -rf /lib/systemd/system/alist.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/alist/initd/alist ];then
		$serverPath/alist/initd/alist stop
	fi

	if [ -d $serverPath/alist ];then
		rm -rf $serverPath/alist
	fi
	
	echo "卸载alist成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
