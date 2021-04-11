#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl

SYSOS=`uname`

Install_aria2()
{
	isStart=""
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/aria2
	echo '1.0' > $serverPath/aria2/version.pl

	if [ "Darwin" == "$SYSOS" ];then
		echo 'macosx unavailable' > $install_tmp
		find_sh=`which aria2c`
		if [ "$?" != "0" ];then
			brew install aria2
		fi
	else
		find_sh=`which aria2c`
		if [ "$?" != "0" ];then
			yum install aria2 -y
		fi
	fi

	echo 'Install complete' > $install_tmp
}

Uninstall_aria2()
{
	rm -rf $serverPath/aria2
	echo "Uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_aria2
else
	Uninstall_aria2
fi
