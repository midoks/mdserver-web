#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2


bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

Install_app()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/supervisor
	mkdir -p $serverPath/supervisor/log
	mkdir -p $serverPath/supervisor/run

	echo 'supervisor install...'
	if [ "centos" == "$OSNAME" ] || [ "fedora" == "$OSNAME" ];then
    	pip install  supervisor
    elif [ "ubuntu" == "$OSNAME" ] || [ "debian" == "$OSNAME" ] ;then
    	pip install supervisor
	else
		pip install supervisor
    	# brew install supervisor
	fi

	echo "${VERSION}" > $serverPath/supervisor/version.pl
	echo '安装完成[supervisor]' > $install_tmp

	cd ${rootPath} && python3 ${rootPath}/plugins/supervisor/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/supervisor/index.py initd_install
}

Uninstall_app()
{

	if [ -f /usr/lib/systemd/system/supervisor.service ] || [ -f /lib/systemd/system/supervisor.service ];then
		systemctl stop supervisor
		systemctl disable supervisor
		rm -rf /usr/lib/systemd/system/supervisor.service
		rm -rf /lib/systemd/system/supervisor.service
		systemctl daemon-reload
	fi

	pip uninstall supervisor -y

	rm -rf $serverPath/supervisor

	echo "卸载完成[supervisor]" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app
else
	Uninstall_app
fi
