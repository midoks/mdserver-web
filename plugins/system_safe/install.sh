#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
SYSOS=`uname`
VERSION=$2
APP_NAME=system_safe

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/system_safe
	echo "$VERSION" > $serverPath/system_safe/version.pl
	echo 'install complete' > $install_tmp

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
	echo "uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
