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

version=8.1.x
PHP_VER=81

Install_php_CentOS(){
### centos start ################
rpm -Uvh http://rpms.remirepo.net/enterprise/remi-release-#{VERSION_ID}.rpm
yum install php81
### centos start ################
}

Uninstall_php_CentOS(){
### centos start ################
echo "uninstall centos"
### centos start ################
}


Install_php()
{
#------------------------ install start ------------------------------------#


if [ "$OSNAME" == 'centos' ];then
	Install_php_CentOS
fi

#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
	if [ "$OSNAME" == 'centos' ];then
		Uninstall_php_CentOS
	fi

	# $serverPath/php-ya/init.d/php${PHP_VER} stop
	rm -rf $serverPath/php-ya/${PHP_VER}
	echo "卸载php-${version}..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
