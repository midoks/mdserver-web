#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/gorse && bash install.sh install 0.4.15
# cd /www/server/mdserver-web/plugins/gorse && bash install.sh install 0.4.15

VERSION=$2

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/gorse

	SYSNAME=linux
	if [ "$sysName" == "Darwin" ];then
		SYSNAME=darwin
	fi

	ARCH="amd64"
	if [ "$sysArch" == "x86_64" ];then
		ARCH="amd64"
	elif [ "$sysArch" == "aarch64" ];then
		ARCH="arm64"
	elif [ "$sysArch" == "arm64" ];then
		ARCH="arm64"
	else
		ARCH="amd64"
	fi

	FILE_TGZ=gorse_${SYSNAME}_${ARCH}.zip
	GORSE_DIR=$serverPath/source/gorse

	# https://github.com/gorse-io/gorse/releases/download/v0.4.15/gorse_linux_amd64.zip
	echo "https://github.com/gorse-io/gorse/releases/download/v${VERSION}/${FILE_TGZ}"

	if [ ! -f $GORSE_DIR/${FILE_TGZ} ];then
		wget -O $GORSE_DIR/${FILE_TGZ} https://github.com/gorse-io/gorse/releases/download/v${VERSION}/${FILE_TGZ}
	fi
	
	mkdir -p $serverPath/gorse/bin
	mkdir -p $serverPath/gorse/logs
	cd $GORSE_DIR && unzip -d $serverPath/gorse/bin ${FILE_TGZ}

	mkdir -p $serverPath/gorse/data
	echo "${VERSION}" > $serverPath/gorse/version.pl
	echo '安装Gorse完成'
	cd ${rootPath} && python3 ${rootPath}/plugins/gorse/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/gorse/index.py initd_install

	if [ -d ${GORSE_DIR}/gorse-${VERSION} ];then
		rm -rf ${GORSE_DIR}/gorse-${VERSION}
	fi
}

Uninstall_App()
{
	app_name=gorse
	systemctl_dir=/lib/systemd/system
	if [ -d /usr/lib/systemd/system ];then
		systemctl_dir=/usr/lib/systemd/system
	fi

	if [ -f ${systemctl_dir}/${app_name}.service ];then
		systemctl stop ${app_name}
		systemctl disable ${app_name}
		rm -rf ${systemctl_dir}/${app_name}.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/${app_name}/initd/${app_name} ];then
		$serverPath/${app_name}/initd/${app_name} stop
	fi

	if [ -d $serverPath/${app_name} ];then
		rm -rf $serverPath/${app_name}
	fi
	
	echo "卸载Gorse成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
