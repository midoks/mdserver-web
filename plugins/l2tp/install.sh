#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl
SYSOS=`uname`

Install_l2tp()
{
	isStart=""
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/l2tp
	echo '1.0' > $serverPath/l2tp/version.pl

	if [ "Darwin" == "$SYSOS" ];then
		echo 'macosx unavailable' > $install_tmp
		exit 0 
	fi

	echo 'install complete' > $install_tmp
}

Uninstall_l2tp()
{
	rm -rf $serverPath/l2tp
	echo "Uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_l2tp
else
	Uninstall_l2tp
fi
