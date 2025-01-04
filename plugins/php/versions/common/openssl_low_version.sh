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
SYS_ARCH=`arch`
actionType=$1
version=$2

LIBNAME=openssl
LIBV=0

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
	
	# cd ${rootPath}/plugins/php/lib && /bin/bash openssl_10.sh
	if [ "$version" -lt "81" ];then
		cd ${rootPath}/plugins/php/lib && /bin/bash openssl_10.sh
	fi

	if [ "$version" -gt "82" ];then
		cd ${rootPath}/plugins/php/lib && /bin/bash openssl.sh
	fi

	if [ "$sysName" == "Darwin" ] ;then 
		BREW_DIR=`which brew`
		BREW_DIR=${BREW_DIR/\/bin\/brew/}

		LIB_DEPEND_DIR=`brew info openssl@1.0 | grep ${BREW_DIR}/Cellar/openssl | cut -d \  -f 1 | awk 'END {print}'`
		export PKG_CONFIG_PATH=$LIB_DEPEND_DIR/lib/pkgconfig
	fi

	if [ ! -f "$extFile" ];then

		if [ ! -d $sourcePath/php${version}/ext ];then
			cd ${rootPath}/plugins/php && /bin/bash ${rootPath}/plugins/php/versions/${version}/install.sh install
		fi

		cd $sourcePath/php${version}/ext/${LIBNAME}

		if [ ! -f "config.m4" ];then
			mv config0.m4 config.m4
		fi
		
		OPTIONS=""
		if [ "${SYS_ARCH}" == "aarch64" ] && [ "$version" -lt "56" ];then
			OPTIONS="$OPTIONS --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu"
		fi

		# openssl_version=`pkg-config openssl --modversion`
		# export PKG_CONFIG_PATH=$serverPath/lib/openssl10/lib/pkgconfig
		if [ "$version" -lt "81" ] && [ "$sysName" != "Darwin" ];then
			export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$serverPath/lib/openssl10/lib/pkgconfig
		fi

		# Darwin
		# otool -L /Users/midoks/Desktop/mwdev/server/php/83/bin/php
		# lldb /Users/midoks/Desktop/mwdev/server/php/83/bin/php -r 'phpinfo()'
		# otool -L /Users/midoks/Desktop/mwdev/server/php/83/lib/php/extensions/no-debug-non-zts-20230831/openssl.so 
		# ldd /www/server/php/83/bin/php

		if [ "$version" -lt "84" ] && [ "$sysName" == "Darwin" ];then
			BREW_DIR=`which brew`
			BREW_DIR=${BREW_DIR/\/bin\/brew/}
			LIB_DEPEND_DIR=`brew info openssl@1.0 | grep ${BREW_DIR}/Cellar/openssl@1.0 | cut -d \  -f 1 | awk 'END {print}'`
			OPTIONS="$OPTIONS --with-openssl=$(brew --prefix openssl@1.0)"
			export PKG_CONFIG_PATH=$LIB_DEPEND_DIR/lib/pkgconfig
			export OPENSSL_CFLAGS="-I${LIB_DEPEND_DIR}/include"
			export OPENSSL_LIBS="-L/${LIB_DEPEND_DIR}/lib -lssl -lcrypto -lz"

			echo "$LIB_DEPEND_DIR/lib/pkgconfig"
		fi

		if [ "$version" -ge "84" ] &&  [ "$sysName" == "Darwin" ];then
			BREW_DIR=`which brew`
			BREW_DIR=${BREW_DIR/\/bin\/brew/}
			LIB_DEPEND_DIR=`brew info openssl | grep ${BREW_DIR}/Cellar/openssl | cut -d \  -f 1 | awk 'END {print}'`
			OPTIONS="$OPTIONS --with-openssl=$(brew --prefix openssl)"
			export PKG_CONFIG_PATH=$LIB_DEPEND_DIR/lib/pkgconfig
			export OPENSSL_CFLAGS="-I${LIB_DEPEND_DIR}/include"
			export OPENSSL_LIBS="-L/${LIB_DEPEND_DIR}/lib -lssl -lcrypto -lz"
		fi

		# if [ "$version" -gt "82" ] && [ "$sysName" == "Darwin" ];then
		# 	export PKG_CONFIG_PATH=$serverPath/lib/openssl/lib/pkgconfig
		# fi

		
		$serverPath/php/$version/bin/phpize
		# --with-openssl
		echo "./configure --with-php-config=$serverPath/php/$version/bin/php-config $OPTIONS"
		./configure --with-php-config=$serverPath/php/$version/bin/php-config $OPTIONS
		make clean && make && make install && make clean

		if [ -d $sourcePath/php${version} ];then
			cd ${sourcePath} && rm -rf $sourcePath/php${version}
		fi
		
	fi

	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

    echo "" >> $serverPath/php/$version/etc/php.ini
	echo "[${LIBNAME}]" >> $serverPath/php/$version/etc/php.ini
	echo "extension=${LIBNAME}.so" >> $serverPath/php/$version/etc/php.ini
	if [ -f "/etc/ssl/certs/ca-certificates.crt" ];then
		echo "openssl.cafile=/etc/ssl/certs/ca-certificates.crt" >> $serverPath/php/$version/etc/php.ini
	elif [ -f "/etc/pki/tls/certs/ca-bundle.crt" ];then
		echo "openssl.cafile=/etc/pki/tls/certs/ca-bundle.crt" >> $serverPath/php/$version/etc/php.ini
	fi
	
	cd  ${curPath} && bash ${rootPath}/plugins/php/versions/lib.sh $version restart
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
	cd  ${curPath} && bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==============================================='
	echo 'successful!'
}



if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi