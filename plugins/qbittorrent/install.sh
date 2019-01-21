#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/bt_install.pl


Install_qbittorrent()
{
	if [ $sysName == 'Darwin' ]; then
		echo 'apple system'
	else
		yum -y install qbittorrent-nox
	fi

	pip install python-qbittorrent

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/qbittorrent

	QB_DIR=${serverPath}/source/qbittorrent
	mkdir -p $QB_DIR

	

	echo '4.1.5' > $serverPath/qbittorrent/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_qbittorrent()
{
	rm -rf $serverPath/qbittorrent
	echo "Uninstall_qbittorrent" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_qbittorrent
else
	Uninstall_qbittorrent
fi
