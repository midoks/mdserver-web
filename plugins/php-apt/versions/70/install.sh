#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`
install_tmp=${rootPath}/tmp/mw_install.pl


#获取信息和版本
# bash /www/server/mdsever-web/scripts/getos.sh
bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

version=7.0
PHP_VER=70


Install_php()
{
#------------------------ install start ------------------------------------#
apt -y install php${version} php${version}-fpm php${version}-dev
if [ "$?" == "0" ];then
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

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
