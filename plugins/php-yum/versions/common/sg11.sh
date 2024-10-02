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

# https://www.sourceguardian.com/loaders.html

# support 52-83

LIBNAME=sg11
LIBV=0

sysName=`uname`
actionType=$1
version=$2
SG_VER=${version:0:1}.${version:1:2}


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
	bash ${rootPath}/scripts/getos.sh
	OSNAME=`cat ${rootPath}/data/osname.pl`
	if [ "$OSNAME" == 'macos' ];then
		VERSION_ID=none
	else
		VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
	fi
	
	echo "${OSNAME}:${VERSION_ID}"

	DEFAULT_OSNAME=linux-x86_64
	SUFFIX_NAME=lin
	if [ "$OSNAME" == 'macos' ];then
		DEFAULT_OSNAME=macosx
		SUFFIX_NAME=dar
	fi
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib

		mkdir -p $php_lib
		mkdir -p $php_lib/sg11

		if [ ! -f $php_lib/sg11_loaders.tar.bz2 ];then
			curl -sSLo $php_lib/sg11_loaders.tar.bz2 https://www.sourceguardian.com/loaders/download/loaders.tar.bz2
			echo "cd $php_lib && tar -jxvf $php_lib/sg11_loaders.tar.bz2 -C $php_lib/sg11"
			cd $php_lib && tar -jxvf $php_lib/sg11_loaders.tar.bz2 -C $php_lib/sg11
		fi 


		if [ ! -d $php_lib/sg11/macosx ];then
			cd $php_lib && tar -jxvf $php_lib/sg11_loaders.tar.bz2 -C $php_lib/sg11
		fi
		cd $php_lib/sg11


		if [ -f $php_lib/sg11/${DEFAULT_OSNAME}/ixed.${SG_VER}.${SUFFIX_NAME} ];then
			cp -rf $php_lib/sg11/${DEFAULT_OSNAME}/ixed.${SG_VER}.${SUFFIX_NAME} $extSoFile
		else
			echo 'Not supported temporarily'
			exit
		fi

		if [ "$OSNAME" == 'macos' ];then
			xattr -c * $extSoFile
		fi
	fi
	
	if [ ! -f "$extSoFile" ];then
		echo "ERROR!"
		return
	fi

	echo  "" >> $extIni
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