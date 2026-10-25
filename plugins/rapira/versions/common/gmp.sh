#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`

appPath=$(dirname "$curPath")

rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/rapira

actionType=$1
version=$2

LIBNAME=gmp
LIBV=0

if [ "$version" = "53" ];then
	echo "i wont support it"
	exit
fi


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

	isInstall=`cat ${phpini}|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then

		if [ ! -d $sourcePath/php${version}/ext ];then
			cd ${rootPath}/plugins/rapira && /bin/bash ${rootPath}/plugins/rapira/versions/${version}/install.sh install 
		fi

		cd $sourcePath/php${version}/ext/${LIBNAME}
		
		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/rapira/$version/link/bin/php-config

		# FIND_C99=`cat Makefile|grep c99`
		# if [ "$FIND_C99" = "" ];then
		# 	sed -i $BAK 's/CFLAGS \=/CFLAGS \= -std=c99/g' Makefile
		# fi

		if [ "$sysName" = "Darwin" ];then
			OPTIONS="$OPTIONS --with-gmp=$(brew --prefix gmp)"
		fi

		make clean && make && make install && make clean
		
		if [ -d $sourcePath/php${version} ];then
			cd ${sourcePath} && rm -rf $sourcePath/php${version}
		fi
	fi

	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

    echo "" >> $phpini
	echo "[${LIBNAME}]" >> $phpini
	echo "extension=${LIBNAME}.so" >> $phpini
	
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