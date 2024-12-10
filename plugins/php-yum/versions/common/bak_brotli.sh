#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

actionType=$1
version=$2

sysName=`uname`
LIBNAME=brotli
LIBV=0.15.2

SORT_LIBNAME="10-${LIBNAME}"
extVer=`bash $curPath/lib.sh $version`
extFile=/opt/remi/php${version}/root/usr/lib64/php
extSoFile=$extFile/modules/${LIBNAME}.so
cfgDir=/etc/opt/remi/php${version}/php.d
extIni=${cfgDir}/10-${LIBNAME}.ini

if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

Install_lib()
{

	isInstall=`cat /etc/php/${version}/fpm/conf.d/* | grep -v '^;' |tr -s '\n' |grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib
		if [ ! -d $php_lib/${LIBNAME}-${LIBV} ];then
			wget -O $php_lib/${LIBNAME}-${LIBV}.tgz http://pecl.php.net/get/${LIBNAME}-${LIBV}.tgz
			cd $php_lib && tar xvf ${LIBNAME}-${LIBV}.tgz
		fi 
		cd $php_lib/${LIBNAME}-${LIBV}

		/opt/remi/php${version}/root/usr/bin/phpize
		./configure --with-php-config=/opt/remi/php${version}/root/usr/bin/
		make && make install && make clean

	fi
	echo "$extFile checking ..."
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return;
	fi
	
	cho  "" >> $extIni
	echo  "[${LIBNAME}]" >> $extIni
	echo "extension=${LIBNAME}.so" >> $extIni
	
	systemctl restart php${version}-fpm 
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{	
	if [ -f $extIni ];then
		rm -rf $extIni
	fi

	systemctl restart php${version}-fpm 
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi