#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl


Install_pg()
{
	echo '卸载PHP守护中...'
	echo 'True' > ${rootPath}/data/502Task.pl

	mkdir -p $serverPath/php-guard
	echo '1.0' > $serverPath/php-guard/version.pl	
	echo '卸载PHP守护成功!!'
}

Uninstall_pg()
{
	rm -rf ${rootPath}/data/502Task.pl
	rm -rf $serverPath/php-guard
	echo '卸载PHP守护成功!!'
}


action=$1
host=$2
if [ "${1}" == 'install' ];then
	Install_pg
else
	Uninstall_pg
fi
