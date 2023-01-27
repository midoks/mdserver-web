#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=1.0

Install_App(){
	mkdir -p $serverPath/migration_api
	echo "${VERSION}" > $serverPath/migration_api/version.pl
	echo '正在安装脚本文件...' > $install_tmp
}

Uninstall_App()
{
	rm -rf $serverPath/migration_api
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
