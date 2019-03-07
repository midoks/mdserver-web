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
extFile=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20090626/${LIBNAME}.so

Install_lib()
{
	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_${version}_lib
		mkdir -p $php_lib

		wget -O $php_lib/zendopcache-7.0.5.tgz http://pecl.php.net/get/zendopcache-7.0.5.tgz

		cd $php_lib && tar xvf zendopcache-7.0.5.tgz
		cd zendopcache-7.0.5
		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config
		make && make install

		cd $php_lib
		rm -rf zendopcache-7.0.5
		rm -rf zendopcache-7.0.5.tgz
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

	echo "" >> $serverPath/php/$version/etc/php.ini
	echo "[opcache]" >> $serverPath/php/$version/etc/php.ini
	echo "extension=${LIBNAME}.so" >> $serverPath/php/$version/etc/php.ini
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
	if [ ! -f "$serverPath/php/$version/bin/php-config" ];then
		echo "php$version 未安装,请选择其它版本!"
		return
	fi
	
	sed -i '_bak' "/${LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i '_bak' "/${LIBNAME}/d" $serverPath/php/$version/etc/php.ini

	if [ ! -f "$extFile" ];then
		echo "php$version 未安装${LIBNAME},请选择其它版本!"
		echo "php-$version not install ${LIBNAME}, Plese select other version!"
		return
	fi
	
	sed -i '_bak' "/${LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i '_bak' "/${LIBNAME}/d" $serverPath/php/$version/etc/php.ini
		
	rm -f $extFile

	$serverPath/php/init.d/php$version reload
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi