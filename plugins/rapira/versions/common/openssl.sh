#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`

rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/rapira
SYS_ARCH=`arch`
actionType=$1
version=$2

LIBNAME=openssl
LIBV=0

LIB_PATH_NAME=lib/php
if [ -d $serverPath/rapira/${version}/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/rapira/${version}/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/rapira/${version}/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

sysName=`uname`
if [ "$sysName" = "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

phpini=$serverPath/rapira/$version/php.ini

Install_lib()
{
	if [ "$version" -lt "70" ];then
		bash $curPath/openssl_low_version.sh $actionType $version
		return 
	fi


	isInstall=`cat ${phpini}|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi

	if [ ! -f "$extFile" ];then
		echo "locked" > $extFile
	fi

    echo "" >> $phpini
	echo "[${LIBNAME}]" >> $phpini
	if [ -f "/etc/ssl/certs/ca-certificates.crt" ];then
		echo "openssl.cafile=/etc/ssl/certs/ca-certificates.crt" >> $phpini
	elif [ -f "/etc/pki/tls/certs/ca-bundle.crt" ];then
		echo "openssl.cafile=/etc/pki/tls/certs/ca-bundle.crt" >> $phpini
	fi
	
	cd  ${curPath} && bash ${rootPath}/plugins/rapira/versions/lib.sh $version restart
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "$serverPath/rapira/$version/link/bin/php-config" ];then
		echo "php-$version 未安装,请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then
		echo "php-$version 未安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	sed -i $BAK "/${LIBNAME}.so/d" $phpini
	sed -i $BAK "/${LIBNAME}/d" $phpini
		
	rm -f $extFile
	cd  ${curPath} && bash ${rootPath}/plugins/rapira/versions/lib.sh $version restart
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" = 'install' ];then
	Install_lib
elif [ "$actionType" = 'uninstall' ];then
	Uninstall_lib
fi