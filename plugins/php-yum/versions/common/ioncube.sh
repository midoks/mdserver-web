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

if [ `echo "$version > 82"|bc` -eq 1 ];then
	echo "I won't support it"
	exit 0
fi

SORT_LIBNAME="10-${LIBNAME}"
extVer=`bash $curPath/lib.sh $version`
extFile=/opt/remi/php${version}/root/usr/lib64/php
extSoFile=$extFile/modules/${LIBNAME}.so
cfgDir=/etc/opt/remi/php${version}/php.d
extIni=${cfgDir}/10-${LIBNAME}.ini

echo $extSoFile
echo $extIni

if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi


min_ver=${version:0:1}.${version:1:2}

Install_lib()
{

	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib
		if [ ! -f $php_lib/ioncube_loaders_lin.tar.gz ];then
			wget -O $php_lib/ioncube_loaders_lin.tar.gz https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz
			cd $php_lib && tar -zxvf ioncube_loaders_lin.tar.gz
		fi 
		cd $php_lib/ioncube
		
		cp -rf $php_lib/ioncube/ioncube_loader_lin_${min_ver}.so $extSoFile

	fi

	echo "$extSoFile checking ..."
	if [ ! -f "$extSoFile" ];then
		echo "ERROR!"
		return;
	fi
	
	echo  "" >> $extIni
	echo  "[${LIBNAME}]" >> $extIni
	echo "zend_extension=${LIBNAME}.so" >> $extIni
	
	systemctl restart php${version}-fpm 
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{

	if [ -f $extIni ];then
		rm -rf $extIni
	fi

	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi