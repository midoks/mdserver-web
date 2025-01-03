#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

SYSOS=`uname`
VERSION=$2
APP_NAME=system_safe

# cd /www/server/mdserver-web && python3 plugins/system_safe/system_safe.py stop 1.0

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/system_safe
	echo "$VERSION" > $serverPath/system_safe/version.pl
	echo 'install complete'

	#初始化 
	cd ${serverPath}/mdserver-web && python3 plugins/system_safe/system_safe.py start $VERSION
	cd ${serverPath}/mdserver-web && python3 plugins/system_safe/system_safe.py initd_install $VERSION
}

Uninstall_App()
{
	
	if [ -f /usr/lib/systemd/system/${APP_NAME}.service ] || [ -f /lib/systemd/system/${APP_NAME}.service ] ;then
		systemctl stop ${APP_NAME}
		systemctl disable ${APP_NAME}
		rm -rf /usr/lib/systemd/system/${APP_NAME}.service
		rm -rf /lib/systemd/system/${APP_NAME}.service
		systemctl daemon-reload
	fi

	rm -rf $serverPath/system_safe
	echo "uninstall completed"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
