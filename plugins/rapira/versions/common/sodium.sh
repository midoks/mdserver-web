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


actionType=$1
version=$2

sysName=`uname`
LIBNAME=sodium
LIBV=2.0.23


LIB_PATH_NAME=lib/php
if [ -d $serverPath/php/${version}/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/php/${version}/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/php/${version}/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

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

	if [ "$sysName" != "Darwin" ];then
		cd ${rootPath}/plugins/rapira/lib && bash libsodium.sh
	fi
	
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib
		if [ ! -d $php_lib/${LIBNAME}-${LIBV} ];then
			if [ ! -f $php_lib/${LIBNAME}-${LIBV}.tgz ];then
				wget -O $php_lib/${LIBNAME}-${LIBV}.tgz http://pecl.php.net/get/lib${LIBNAME}-${LIBV}.tgz
			fi
			cd $php_lib && tar xvf ${LIBNAME}-${LIBV}.tgz
		fi
		cd $php_lib/lib${LIBNAME}-${LIBV}


		OPTIONS=""
		if [ "$sysName" = "Darwin" ];then
			BREW_DIR=`which brew`
			BREW_DIR=${BREW_DIR/\/bin\/brew/}
			LIB_DEPEND_DIR=`brew info libsodium | grep ${BREW_DIR}/Cellar/libsodium | cut -d \  -f 1 | awk 'END {print}'`
			OPTIONS="$OPTIONS --with-sodium=${LIB_DEPEND_DIR}"
		else
			OPTIONS="$OPTIONS --with-sodium=$serverPath/lib/libsodium"
		fi

		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config $OPTIONS
		make clean && make && make install && make clean

		if [ -d $php_lib/lib${LIBNAME}-${LIBV} ];then
			cd $php_lib && rm -rf $php_lib/lib${LIBNAME}-${LIBV}
		fi
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi
	
	echo  "" >> $phpini
	echo  "[${LIBNAME}]" >> $phpini
	echo  "extension=${LIBNAME}.so" >> $phpini
	
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