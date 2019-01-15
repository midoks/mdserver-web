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

LIBNAME=ZendGuardLoader

sysName=`uname`

Install_lib()
{
	

	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	extFile=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20131226/${LIBNAME}.so
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_${version}_lib
		mkdir -p $php_lib

		if [ $sysName == 'Darwin' ]; then
			wget -O $php_lib/zend-loader-php5.6.tar.gz http://downloads.zend.com/guard/7.0.0/zend-loader-php5.6-darwin10.7-x86_64_update1.tar.gz
		else
			wget -O $php_lib/zend-loader-php5.6.tar.gz http://downloads.zend.com/guard/7.0.0/zend-loader-php5.6-linux-x86_64_update1.tar.gz
		fi 


		cd $php_lib && tar xvf zend-loader-php5.6.tar.gz
		cd zend-loader-php5.6*
		cp ZendGuardLoader.so $serverPath/php/$version/lib/php/extensions/no-debug-non-zts-20131226/

		rm -rf $php_lib/zend-loader-php5.6*
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

	echo -e "[Zend ZendGuard Loader]\nzend_extension=ZendGuardLoader.so\nzend_loader.enable=1\nzend_loader.disable_licensing=0\nzend_loader.obfuscation_level_support=3\nzend_loader.license_path=" >> $serverPath/php/$version/etc/php.ini
	
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
	
	extFile=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20131226/${LIBNAME}.so
	if [ ! -f "$extFile" ];then
		echo "php$version 未安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	sed -i '_bak' '/ZendGuardLoader.so/d'  $serverPath/php/$version/etc/php.ini
	sed -i '_bak' '/zend_loader/d'  $serverPath/php/$version/etc/php.ini
	sed -i '_bak' '/\[Zend ZendGuard Loader\]/d'  $serverPath/php/$version/etc/php.ini
		
	rm -f $extFile
	$serverPath/php/init.d/php$version reload
	echo '==============================================='
	echo 'successful!'
}


actionType=$1
version=$2
if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi