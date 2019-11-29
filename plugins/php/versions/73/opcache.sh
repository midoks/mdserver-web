#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`

rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

LIBNAME=opcache
LIBV=7.0.5
sysName=`uname`
actionType=$1
version=$2
extFile=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20180731/${LIBNAME}.so

Install_lib()
{
	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi

	echo "" >> $serverPath/php/$version/etc/php.ini
	echo "[opcache]" >> $serverPath/php/$version/etc/php.ini
	echo "zend_extension=${LIBNAME}.so" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.enable=1" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.memory_consumption=128" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.interned_strings_buffer=8" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.max_accelerated_files=4000" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.revalidate_freq=60" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.fast_shutdown=1" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.enable_cli=1" >> $serverPath/php/$version/etc/php.ini

	$serverPath/php/init.d/php$version reload
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{	
	sed -i '_bak' "/${LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i '_bak' "/${LIBNAME}/d" $serverPath/php/$version/etc/php.ini
		
	$serverPath/php/init.d/php$version reload
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi