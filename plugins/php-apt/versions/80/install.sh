#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

action=${1}

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`

#获取信息和版本
# bash /www/server/mdsever-web/scripts/getos.sh
bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

version=8.0
PHP_VER=80


Install_php()
{
#------------------------ install start ------------------------------------#
if [ "$action" == "upgrade" ];then
	apt -y upgrade php${version} php${version}-fpm php${version}-dev
else
	apt -y install php${version} php${version}-fpm php${version}-dev
fi

if [ "$?" = "0" ];then
	mkdir -p $serverPath/php-apt/${PHP_VER}
fi


#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
#------------------------ uninstall start ------------------------------------#
apt -y remove php${version} php${version}-*
rm -rf $serverPath/php-apt/${PHP_VER}
echo "卸载php-${version}..."
#------------------------ uninstall start ------------------------------------#
}

if [ "${action}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_php
elif [ "${1}" = 'uninstall' ];then
	Uninstall_php
else
	echo "OPTIONS ERROR"
fi
