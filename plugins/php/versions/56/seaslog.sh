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

LIBNAME=SeasLog
_LIBNAME=$(echo $LIBNAME | tr '[A-Z]' '[a-z]')
LIBV=2.0.2
sysName=`uname`
actionType=$1
version=$2

extDir=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20131226/

if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

Install_lib()
{
	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep "${_LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	extFile=$extDir${_LIBNAME}.so
	if [ ! -f "$extFile" ];then
		OPTIONS=''
		if [ $sysName == 'Darwin' ]; then
			OPTIONS="${OPTIONS} --with-curl=${serverPath}/lib/curl"
		fi 

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib
		if [ ! -d $php_lib/${LIBNAME}-${LIBV} ];then
			wget -O $php_lib/${LIBNAME}-${LIBV}.tgz http://pecl.php.net/get/${LIBNAME}-${LIBV}.tgz
			cd $php_lib && tar xvf ${LIBNAME}-${LIBV}.tgz
		fi 
		cd $php_lib/${LIBNAME}-${LIBV}

		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config
		make && make install && make clean

	fi
	sleep 1
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

	_LIBNAME=$(echo $LIBNAME | tr '[A-Z]' '[a-z]')
	echo "" >> $serverPath/php/$version/etc/php.ini
	echo "[${_LIBNAME}]" >> $serverPath/php/$version/etc/php.ini
	echo "extension=${_LIBNAME}.so" >> $serverPath/php/$version/etc/php.ini

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
	
	extFile=$extDir${_LIBNAME}.so
	if [ ! -f "$extFile" ];then
		echo "php-$version 未安装${LIBNAME},请选择其它版本!"
		echo "php-$version not install ${LIBNAME}, Plese select other version!"
		return
	fi
	_LIBNAME=$(echo $LIBNAME | tr '[A-Z]' '[a-z]')
	sed -i $BAK "/${_LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i $BAK "/${_LIBNAME}/d" $serverPath/php/$version/etc/php.ini
		
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