#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/data_query
	echo "${VERSION}" > $serverPath/data_query/version.pl

	echo '安装完成'
}

Uninstall_App()
{
	rm -rf $serverPath/data_query
	echo "卸载成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
