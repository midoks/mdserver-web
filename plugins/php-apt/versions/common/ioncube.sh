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

actionType=$1
version=$2

sysName=`uname`
LIBNAME=ioncube
LIBV=0

if [ `echo "$version > 8.3"|bc` -eq 1 ];then
	echo "I won't support it"
	exit 0
fi


extVer=`bash $curPath/lib.sh $version`
extFile=/usr/lib/php/${extVer}/${LIBNAME}.so

if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

SORT_LIBNAME="10-${LIBNAME}"

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
		if [ ! -f $php_lib/ioncube_loaders_lin.tar.gz ];then
			wget -O $php_lib/ioncube_loaders_lin.tar.gz https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz
			cd $php_lib && tar -zxvf ioncube_loaders_lin.tar.gz
		fi 
		cd $php_lib/ioncube
		
		cp -rf $php_lib/ioncube/ioncube_loader_lin_${version}.so $extFile

	fi

	echo "$extFile checking ..."
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return;
	fi
	
	echo  "" >> /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini
	echo  "[${LIBNAME}]" >> /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini
	echo "zend_extension=${LIBNAME}.so" >> /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini
	
	systemctl restart php${version}-fpm 
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "/usr/bin/php-config${version}" ];then
		echo "php-$version 未安装,请选择其它版本!"
		return
	fi

	
	if [ -f /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini ];then
		rm -rf /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini
		rm -rf $extFile
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