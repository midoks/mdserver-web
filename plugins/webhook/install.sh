#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=1.0

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/webhook
	echo "${VERSION}" > $serverPath/webhook/version.pl
	echo '安装完成'
}

Uninstall_App()
{
	rm -rf $serverPath/webhook
	echo "Uninstall_App"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
