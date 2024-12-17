# -*- coding: utf-8 -*-
#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
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
MYSQL_VER=5.7.44
SUFFIX_NAME=${MYSQL_VER}-linux-glibc2.12-${OS_ARCH}

if [ "$OS_ARCH" == "x86_64" ] || [ "$OS_ARCH" == "i686" ];then
	echo "ok"
else
	echo "暂时不支持该${OS_ARCH}"
	exit 0
fi

# cd /www/server/mdserver-web/plugins/mysql-community && bash install.sh install 5.7
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql-community/index.py start 5.7
COMMUNITY_INSTALL()
{

########
mkdir -p $myDir
mkdir -p $serverPath/mysql-community

# Linux - Generic
if [ ! -f ${myDir}/mysql-${SUFFIX_NAME}.tar.gz ];then
	wget --no-check-certificate -O ${myDir}/mysql-${SUFFIX_NAME}.tar.gz https://cdn.mysql.com/archives/mysql-5.7/mysql-${SUFFIX_NAME}.tar.gz
fi

if [ -d ${myDir} ];then
	cd ${myDir} && tar -zvxf ${myDir}/mysql-${SUFFIX_NAME}.tar.gz
	cp -rf ${myDir}/mysql-${SUFFIX_NAME}/* $serverPath/mysql-community
fi

# 测试时可关闭
rm -rf $myDir/mysql-${SUFFIX_NAME}
#######
}

COMMUNITY_UNINSTALL()
{
###
rm -rf $myDir/mysql-${SUFFIX_NAME}
###
}


Install_mysql()
{
	echo '正在安装脚本文件...'
	COMMUNITY_INSTALL
	if [ "$?" == "0" ];then
		mkdir -p $serverPath/mysql-community
		echo '5.7' > $serverPath/mysql-community/version.pl
		echo '安装完成'
	else
		echo '5.7' > $serverPath/mysql-community/version.pl
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
if [ "${1}" == 'install' ];then
	Install_mysql
else
	Uninstall_mysql
fi
