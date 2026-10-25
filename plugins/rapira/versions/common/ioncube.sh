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

# support 55-74

LIBNAME=ioncube
LIBV=0
sysName=`uname`
actionType=$1
version=$2
IC_VERSION=${version:0:1}.${version:1:2}
ARCH=`uname -m`

if [ "$version" -gt "82" ];then
	echo "not need"
	exit 1
fi

DEFAULT_ARCH='x86-64'
if [ "$ARCH" = "aarch64" ];then
	DEFAULT_ARCH='aarch64'
fi

LIB_PATH_NAME=lib/php
if [ -d $serverPath/rapira/${version}/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/rapira/${version}/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/rapira/${version}/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

if [ "$sysName" = "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

phpini=$serverPath/rapira/$version/php.ini

Install_lib()
{
	isInstall=`cat ${phpini}|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib
		if [ ! -f $php_lib/ioncube_loaders_lin.tar.gz ];then
			wget -O $php_lib/ioncube_loaders_lin.tar.gz https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_${DEFAULT_ARCH}.tar.gz
			cd $php_lib && tar -zxvf ioncube_loaders_lin.tar.gz
		fi 

		if [ ! -d $php_lib/ioncube ];then
			cd $php_lib && tar -zxvf ioncube_loaders_lin.tar.gz
		fi
		cd $php_lib/ioncube
		
		cp -rf $php_lib/ioncube/ioncube_loader_lin_${IC_VERSION}.so $extFile
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

	sed -i $BAK "1i\[${LIBNAME}]" $phpini
	sed -i $BAK "2i\zend_extension=${LIBNAME}.so" $phpini
	# echo "[${LIBNAME}]" >> $phpini
	# echo "zend_extension=${LIBNAME}.so" >> $phpini

	cd  ${curPath} && bash ${rootPath}/plugins/rapira/versions/lib.sh $version restart
	echo '==========================================================='
	echo 'successful!'

	if [ -d $php_lib/ioncube ];then
		rm -rf $php_lib/ioncube
	fi
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