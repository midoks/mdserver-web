#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

Install_bbr()
{
	echo '正在安装脚本文件...' > $install_tmp

	chmod +x $curPath/scripts/bbr.sh
	sh $curPath/scripts/bbr.sh

	mkdir -p $serverPath/bbr
	echo '1.0' > $serverPath/bbr/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_bbr()
{
	rm -rf $serverPath/bbr
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_bbr
else
	Uninstall_bbr
fi
