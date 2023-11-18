#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`

rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php
SYS_ARCH=`arch`
LIBNAME=opcache
LIBV=7.0.5
sysName=`uname`
actionType=$1
version=$2

NON_ZTS_FILENAME=`ls $serverPath/php/${version}/lib/php/extensions | grep no-debug-non-zts`
extFile=$serverPath/php/${version}/lib/php/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

Install_lib()
{
	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib

		if [ ! -d  $php_lib/zendopcache-7.0.5 ];then
			wget -O $php_lib/zendopcache-7.0.5.tgz http://pecl.php.net/get/zendopcache-7.0.5.tgz
			cd $php_lib && tar xvf zendopcache-7.0.5.tgz
		fi
		cd $php_lib/zendopcache-7.0.5

		OPTIONS=''
		if [ "${SYS_ARCH}" == "aarch64" ] && [ "$version" -lt "56" ];then
			OPTIONS="$OPTIONS --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu"
		fi

		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config $OPTIONS
		make && make install && make clean
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi

	echo "" >> $serverPath/php/$version/etc/php.ini
	echo "[${LIBNAME}]" >> $serverPath/php/$version/etc/php.ini
	echo "zend_extension=${LIBNAME}.so" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.enable=1" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.memory_consumption=128" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.interned_strings_buffer=8" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.max_accelerated_files=4000" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.revalidate_freq=60" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.fast_shutdown=1" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.enable_cli=1" >> $serverPath/php/$version/etc/php.ini

	bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "$serverPath/php/$version/bin/php-config" ];then
		echo "php-$version 未安装,请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then
		echo "php-$version 未安装${LIBNAME},请选择其它版本!"
		echo "php-$version not install ${LIBNAME}, Plese select other version!"
		return
	fi
	
	sed -i $BAK "/${LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i $BAK "/${LIBNAME}/d" $serverPath/php/$version/etc/php.ini
		
	rm -f $extFile

	bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi