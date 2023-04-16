#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

pip install pyinotify
if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi
pip install pyinotify

install_tmp=${rootPath}/tmp/mw_install.pl
SYSOS=`uname`
VERSION=$2
APP_NAME=tamper_proof_py

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/tamper_proof_py
	echo "$VERSION" > $serverPath/tamper_proof_py/version.pl
	echo 'install complete' > $install_tmp

	#初始化 
	cd ${serverPath}/mdserver-web && python3 plugins/tamper_proof_py/index.py start $VERSION
	cd ${serverPath}/mdserver-web && python3 plugins/tamper_proof_py/index.py initd_install $VERSION
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

	rm -rf $serverPath/tamper_proof_py
	echo "uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
