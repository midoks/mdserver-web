#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`


if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

VERSION=$2

Install_App()
{
	echo '正在安装manticore...'
}

Uninstall_App()
{
	yum -y uninstall manticore manticore-extra

	if [ -d $serverPath/manticoresearch ];then
		rm -rf $serverPath/manticoresearch
	fi

	echo "卸载manticoresearch成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
