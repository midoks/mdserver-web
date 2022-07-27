#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`
install_tmp=${rootPath}/tmp/mw_install.pl


function version_gt() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" != "$1"; }
function version_le() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" == "$1"; }
function version_lt() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" != "$1"; }
function version_ge() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" == "$1"; }

version=7.4.26
PHP_VER=74
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

cd $serverPath/mdserver-web/plugins/php/lib && /bin/bash freetype_new.sh
cd $serverPath/mdserver-web/plugins/php/lib && /bin/bash zlib.sh
cd $serverPath/mdserver-web/plugins/php/lib && /bin/bash libzip.sh

if [ ! -d $sourcePath/php/php${PHP_VER} ];then

	if [ ! -f $sourcePath/php/php-${version}.tar.xz ];then
		wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.xz https://museum.php.net/php7/php-${version}.tar.xz
	fi
	
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-${version}.tar.xz
	mv $sourcePath/php/php-${version} $sourcePath/php/php${PHP_VER}
fi



cd $sourcePath/php/php${PHP_VER}

OPTIONS=''
if [ $sysName == 'Darwin' ]; then
	OPTIONS='--without-iconv'
	OPTIONS="${OPTIONS} --with-curl=${serverPath}/lib/curl"
	# OPTIONS="${OPTIONS} --enable-zip"

	export PATH="/usr/local/opt/bison/bin:$PATH"
	export LDFLAGS="-L/usr/local/opt/bison/lib"
	export PKG_CONFIG_PATH="/usr/local/opt/libxml2/lib/pkgconfig"
	export LDFLAGS="-L/usr/local/opt/libxml2/lib"
else
	OPTIONS='--without-iconv'
	OPTIONS="${OPTIONS} --with-curl"
fi

IS_64BIT=`getconf LONG_BIT`
if [ "$IS_64BIT" == "64" ];then
	OPTIONS="${OPTIONS} --with-libdir=lib64"
fi

echo "$sourcePath/php/php${PHP_VER}"

ZIP_OPTION='--with-zip'
libzip_version=`pkg-config libzip --modversion`
if version_lt "$libzip_version" "0.11.0" ;then
	export PKG_CONFIG_PATH=$serverPath/lib/libzip/lib/pkgconfig
	ZIP_OPTION="--with-zip=$serverPath/lib/libzip"
fi


if [ ! -d $serverPath/php/${PHP_VER} ];then
	cd $sourcePath/php/php${PHP_VER} && make clean
	./buildconf --force
	./configure \
	--prefix=$serverPath/php/${PHP_VER} \
	--exec-prefix=$serverPath/php/${PHP_VER} \
	--with-config-file-path=$serverPath/php/${PHP_VER}/etc \
	--enable-mysqlnd \
	--with-mysqli=mysqlnd \
	--with-pdo-mysql=mysqlnd \
	--with-zlib-dir=$serverPath/lib/zlib \
	$ZIP_OPTION \
	--enable-ftp \
	--enable-mbstring \
	--enable-sockets \
	--enable-simplexml \
	--enable-soap \
	--enable-posix \
	--enable-sysvmsg \
	--enable-sysvsem \
	--enable-sysvshm \
	--disable-intl \
	--disable-fileinfo \
	$OPTIONS \
	--enable-fpm
	make && make install && make clean
fi 
#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
	$serverPath/php/init.d/php${PHP_VER} stop
	rm -rf $serverPath/php/${PHP_VER}
	echo "卸载php-${version}..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
