#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

# https://www.sourceguardian.com/loaders.html

# support 52-81

LIBNAME=sg11
LIBV=0
sysName=`uname`
actionType=$1
version=$2
# SG_VER=${version:0:1}.${version:1:2}
SG_VER=${version}

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
	bash ${rootPath}/scripts/getos.sh
	OSNAME=`cat ${rootPath}/data/osname.pl`

	echo "${OSNAME}"

	DEFAULT_OSNAME=linux-x86_64
	SUFFIX_NAME=lin
	if [ "$OSNAME" == 'macos' ];then
		DEFAULT_OSNAME=macosx
		SUFFIX_NAME=dar
	fi

	isInstall=`cat /etc/php/${version}/fpm/conf.d/* | grep -v '^;' |tr -s '\n' |grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
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
		# echo "mv $php_lib/sg11/${DEFAULT_OSNAME}/ixed.${SG_VER}.lin $extFile"
		if [ -f $php_lib/sg11/${DEFAULT_OSNAME}/ixed.${SG_VER}.${SUFFIX_NAME} ];then
			cp -rf $php_lib/sg11/${DEFAULT_OSNAME}/ixed.${SG_VER}.${SUFFIX_NAME} $extFile
		else
			echo 'Not supported temporarily'
			exit
		fi

		if [ "$OSNAME" == 'macos' ];then
			xattr -c * $extFile
		fi
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

	echo  "" >> /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini
	echo  "[${LIBNAME}]" >> /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini
	echo "extension=${LIBNAME}.so" >> /etc/php/${version}/fpm/conf.d/${SORT_LIBNAME}.ini
	
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