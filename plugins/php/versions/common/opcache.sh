#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`

rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

LIBNAME=opcache
sysName=`uname`
actionType=$1
version=$2

LIB_PATH_NAME=lib/php
if [ -d $serverPath/php/${version}/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/php/${version}/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/php/${version}/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so


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
	
	# OPcache 黑名单文件位置。 
	# 黑名单文件为文本文件，包含了不进行预编译优化的文件名，每行一个文件名。 
	# 黑名单中的文件名可以使用通配符，也可以使用前缀。 此文件中以分号（;）开头的行将被视为注释。
	OP_BL=${serverPath}/php/opcache-blacklist.txt
	if [ ! -f $OP_BL ];then
		touch $OP_BL
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
	echo "opcache.jit=1205" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.jit_buffer_size=64M" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.save_comments=0" >> $serverPath/php/$version/etc/php.ini
	echo "opcache.blacklist_filename=${OP_BL}" >> $serverPath/php/$version/etc/php.ini

	cd  ${curPath} && bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{	
	sed -i $BAK "/${LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i $BAK "/${LIBNAME}/d" $serverPath/php/$version/etc/php.ini
		
	cd  ${curPath} && bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi