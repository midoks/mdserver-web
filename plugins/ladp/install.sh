#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
sysArch=`arch`

VERSION=$2

# https://juejin.cn/post/7309323953683480588

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/ladp
	apt install -y slapd ldap-utils

	echo "${VERSION}" > $serverPath/ladp/version.pl
	echo "${VERSION}安装完成"
}

Uninstall_App()
{	
	rm -rf $serverPath/ladp/version.pl
	echo "卸载ldap成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
