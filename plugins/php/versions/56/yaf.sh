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

Install_lib()
{
	extFile=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20131226/yaf.so

	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep 'yaf.so'`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装yaf,请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then
		
		wafV='2.3.5';
		if [ "$version" = '70' ] || [ "$version" = '71' ] || [ "$version" = '72' ];then
			wafV='3.0.7';
		fi

		php_lib=$sourcePath/php_${version}_lib
		mkdir -p $php_lib
		wget -O $php_lib/yaf-$wafV.tgz http://pecl.php.net/get/yaf-$wafV.tgz
		cd $php_lib
		tar xvf yaf-$wafV.tgz
		cd yaf-$wafV
		
		echo "$serverPath/php/$version/bin/phpize"
		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config
		make && make install
		cd ..
		rm -rf yaf-*
		rm -f package.xml
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return;
	fi
	echo "extension=$extFile"
	echo "extension=$extFile" >> $serverPath/php/$version/etc/php.ini
	
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
	
	extFile=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20131226/yaf.so
	if [ ! -f "$extFile" ];then
		echo "php$version 未安装yaf,请选择其它版本!"
		return
	fi
	
	echo $serverPath/php/$version/etc/php.ini
	sed -i '_bak' '/yaf.so/d' $serverPath/php/$version/etc/php.ini
		
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