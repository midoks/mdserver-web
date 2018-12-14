#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl


Install_abkill()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/abkill
	echo '安装完成' > $install_tmp
}

Uninstall_abkill()
{
	rm -rf $serverPath/abkill
	echo "Uninstall_redis" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_abkill
else
	Uninstall_abkill
fi
