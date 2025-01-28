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

# 该命令将在本地服务器上查找并返回在 “dc=bytedance,dc=local” 这个起点（和其下的所有子目录）下，所有 cn 属性有值的条目的详细信息
# ldapsearch -x -H ldap://localhost -b "dc=bytedance,dc=local" "(cn=*)"

Install_App()
{
	echo '正在安装脚本文件...'
	apt install -y slapd ldap-utils

	mkdir -p $serverPath/ldap
	echo "${VERSION}" > $serverPath/ldap/version.pl
	echo "${VERSION}安装完成"
}

Uninstall_App()
{	
	rm -rf $serverPath/ldap/version.pl
	echo "卸载ldap成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
