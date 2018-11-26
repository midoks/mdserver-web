#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl

Install_php()
{
	echo '正在安装脚本文件...' > $install_tmp

	echo '安装完成' > $install_tmp
	
}

Uninstall_safelogin()
{
	chattr -i /www/server/panel/plugin/safelogin/token.pl
	rm -f /www/server/panel/data/limitip.conf
	sed -i "/ALL/d" /etc/hosts.deny
	rm -rf /www/server/panel/plugin/safelogin
}


action=$1
host=$2;
if [ "${1}" == 'install' ];then
	Uninstall_php
else
	Uninstall_php
fi
