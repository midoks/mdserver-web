#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
SYSOS=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=$2

Install_swap()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/swap
	echo "${VERSION}" > $serverPath/swap/version.pl

	if [ "$sysName" == "Darwin" ];then
		pass
	else
		dd if=/dev/zero of=/swapfile bs=1M count=1024
		chmod 600 /swapfile
		mkswap /swapfile
		swapon /swapfile
	fi 

	echo '安装完成' > $install_tmp
}

Uninstall_swap()
{
	rm -rf $serverPath/swap
	echo "Uninstall_swap" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_swap
else
	Uninstall_swap
fi
