# -*- coding: utf-8 -*-
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
export DEBIAN_FRONTEND=noninteractive

# https://downloads.mysql.com/archives/community/

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

myDir=${serverPath}/source/mysql-community

OS_ARCH=`arch`
MYSQL_VER=26.10.0
SUFFIX_NAME=${MYSQL_VER}-macos15-arm64

COMMUNITY_INSTALL()
{

########
mkdir -p $myDir
mkdir -p $serverPath/mysql-community

# https://cdn.mysql.com/archives/mysql-26.10/mysql-26.10.0-macos15-arm64.tar.gz
# https://cdn.mysql.com//Downloads/MySQL-26.10/mysql-26.10.0-macos15-arm64.tar.gz
if [ ! -f ${myDir}/mysql-${SUFFIX_NAME}.tar.gz ];then
	# wget --no-check-certificate -O ${myDir}/mysql-${SUFFIX_NAME}.tar.gz https://cdn.mysql.com/archives/mysql-8.2/mysql-${SUFFIX_NAME}.tar.gz
	wget --no-check-certificate -O ${myDir}/mysql-${SUFFIX_NAME}.tar.gz https://cdn.mysql.com//Downloads/MySQL-26.10/mysql-${SUFFIX_NAME}.tar.gz
fi

if [ -d ${myDir} ];then
	cd ${myDir} && tar -zxvf ${myDir}/mysql-${SUFFIX_NAME}.tar.gz
	cp -rf ${myDir}/mysql-${SUFFIX_NAME}/* $serverPath/mysql-community
fi

# 测试时可关闭
# rm -rf $myDir/mysql-${SUFFIX_NAME}
#######
}

COMMUNITY_UNINSTALL()
{
###
rm -rf $myDir/mysql-${SUFFIX_NAME}
# apt remove -y mysql-server
###
}


Install_mysql()
{
	echo '正在安装脚本文件...'
	COMMUNITY_INSTALL
	if [ "$?" = "0" ];then
		mkdir -p $serverPath/mysql-community
		echo '26.10' > $serverPath/mysql-community/version.pl
		echo '安装完成'
	else
		echo '26.10' > $serverPath/mysql-community/version.pl
		echo "暂时不支持该系统"
	fi
}

Uninstall_mysql()
{
	COMMUNITY_UNINSTALL
	rm -rf $serverPath/mysql-community
	echo '卸载完成'
}

action=$1
if [ "${1}" = 'install' ];then
	Install_mysql
else
	Uninstall_mysql
fi
