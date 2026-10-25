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

LIBNAME=fileinfo
LIBV=0

if [ "$version" = "53" ];then
	echo "i wont support it"
	exit
fi

LIB_PATH_NAME=lib/php
if [ -d $serverPath/rapira/${version}/link/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/rapira/${version}/link/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/rapira/${version}/link/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so


sysName=`uname`
if [ "$sysName" = "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

OSNAME=`cat ${rootPath}/data/osname.pl`

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
		
		OPTIONS=''
		if [ "${SYS_ARCH}" = "aarch64" ] && [ "$version" -lt "56" ];then
			OPTIONS="$OPTIONS --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu"
		fi

		
		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/rapira/$version/link/bin/php-config $OPTIONS


		# It is considered as a temporary bug
		if [ "$version" = "81" ] || [ "$version" = "82" ];then
			bash ${rootPath}/scripts/getos.sh
			if [ "$OSNAME" = 'centos' ];then
				FILE_softmagic=$sourcePath/php${version}/ext/${LIBNAME}/libmagic/softmagic.c
				FIND_UNDEF_STRNDUP=`cat $FILE_softmagic|grep '#undef strndup'`
				if [ "$version" -gt "74" ] && [ "$FIND_UNDEF_STRNDUP" = "" ];then
					sed -i $BAK "s/char \*strndup/#undef strndup\nchar \*strndup/g" $FILE_softmagic
				fi
			fi
		fi

		FIND_C99=`cat Makefile|grep c99`
		if [ "$version" -gt "74" ] && [ "$FIND_C99" = "" ];then
			sed -i $BAK 's/CFLAGS \=/CFLAGS \= -std=gnu99/g' Makefile
		fi

		if [ "$version" -gt "80" ] && [ "$OSNAME" = 'centos' ];then
			sed -i $BAK "s#CFLAGS = -g -O2#CFLAGS = -std=c99 -g#g" $sourcePath/php${version}/ext/${LIBNAME}/Makefile
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