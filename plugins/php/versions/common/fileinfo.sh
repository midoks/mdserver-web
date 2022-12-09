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

LIBNAME=fileinfo
LIBV=0

if [ "$version" == "53" ];then
	echo "i wont support it"
	exit
fi

LIB_PATH_NAME=lib/php
if [ -d $serverPath/php/${version}/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/php/${version}/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/php/${version}/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

sysName=`uname`
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
	
	if [ ! -f "$extFile" ];then

		if [ ! -d $sourcePath/php${version}/ext ];then
			echo "cd ${rootPath}/plugins/php && /bin/bash install.sh install ${version}"
			cd ${rootPath}/plugins/php && /bin/bash install.sh install ${version}
		fi

		cd $sourcePath/php${version}/ext/${LIBNAME}
		
		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config


		# It is considered as a temporary bug
		if [ "$version" == "81" ] || [ "$version" == "82" ];then
			bash ${rootPath}/scripts/getos.sh
			OSNAME=`cat ${rootPath}/data/osname.pl`
			if [ "$OSNAME" == 'centos' ];then
				FILE_softmagic=$sourcePath/php${version}/ext/${LIBNAME}/libmagic/softmagic.c
				FIND_UNDEF_STRNDUP=`cat $FILE_softmagic|grep '#undef strndup'`
				if [ "$version" -gt "74" ] && [ "$FIND_UNDEF_STRNDUP" == "" ];then
					sed -i $BAK "s/char \*strndup/#undef strndup\nchar \*strndup/g" $FILE_softmagic
				fi
			fi
		fi

		FIND_C99=`cat Makefile|grep c99`
		if [ "$version" -gt "74" ] && [ "$FIND_C99" == "" ];then
			sed -i $BAK 's/CFLAGS \=/CFLAGS \= -std=gnu99/g' Makefile
		fi

		make clean && make && make install && make clean
		
	fi

	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi


    echo "" >> $serverPath/php/$version/etc/php.ini
	echo "[${LIBNAME}]" >> $serverPath/php/$version/etc/php.ini
	echo "extension=${LIBNAME}.so" >> $serverPath/php/$version/etc/php.ini
	
	bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "$serverPath/php/$version/bin/php-config" ];then
		echo "php-$version 未安装,请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then
		echo "php-$version 未安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	echo $serverPath/php/$version/etc/php.ini
	sed -i $BAK "/${LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i $BAK "/${LIBNAME}/d" $serverPath/php/$version/etc/php.ini
		
	rm -f $extFile
	bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==============================================='
	echo 'successful!'
}



if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi