#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl

npm install pm2 -g

Install_pm2()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/pm2
	echo '1.0' > $serverPath/pm2/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_pm2()
{
	rm -rf $serverPath/pm2
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_pm2
else
	Uninstall_pm2
fi
