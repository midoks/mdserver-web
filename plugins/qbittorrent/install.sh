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
		#安装Nux-Dextop源
		sudo rpm --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro 
		sudo rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-1.el7.nux.noarch.rpm
		yum install -y ffmpeg
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
	which yum && yum -y remove qbittorrent-nox
	echo "Uninstall_qbittorrent" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_qbittorrent
else
	Uninstall_qbittorrent
fi
