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
	echo 'install scripts ...' > $install_tmp


	echo 'True' > ${rootPath}/data/502Task.pl

	mkdir -p $serverPath/php_guard
	echo '1.0' > $serverPath/php_guard/version.pl
	
	echo 'install ok' > $install_tmp
}

Uninstall_pg()
{
	rm -rf ${rootPath}/data/502Task.pl
	rm -rf $serverPath/php_guard
}


action=$1
host=$2
if [ "${1}" == 'install' ];then
	Install_pg
else
	Uninstall_pg
fi
