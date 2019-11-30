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


version=7.4.0
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -d $sourcePath/php/php74 ];then
	wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.gz https://github.com/php/php-src/archive/php-${version}.tar.gz
	cd $sourcePath/php && tar zxvf $sourcePath/php/php-${version}.tar.gz

	mv $sourcePath/php/php-src-php-${version} $sourcePath/php/php74
fi

cd $sourcePath/php/php74

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
	OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-freetype-dir=${serverPath}/lib/freetype"
	OPTIONS="${OPTIONS} --with-gd --enable-gd-native-ttf"
	OPTIONS="${OPTIONS} --with-curl"
	OPTIONS="${OPTIONS} --with-libzip=${serverPath}/lib/libzip"
fi


echo "$sourcePath/php/php-src-php-${version}"

if [ ! -d $serverPath/php/74 ];then
	cd $sourcePath/php/php74
	./buildconf --force
	./configure \
	--prefix=$serverPath/php/74 \
	--exec-prefix=$serverPath/php/74 \
	--with-config-file-path=$serverPath/php/74/etc \
	--enable-mysqlnd \
	--with-mysqli=mysqlnd \
	--with-pdo-mysql=mysqlnd \
	--enable-mbstring \
	--with-zlib-dir=$serverPath/lib/zlib \
	--enable-ftp \
	--enable-sockets \
	--enable-simplexml \
	--enable-intl \
	--enable-soap \
	--enable-posix \
	--enable-sysvmsg \
	--enable-sysvsem \
	--enable-sysvshm \
	--disable-fileinfo \
	$OPTIONS \
	--enable-fpm \
	&& make && make install && make clean
fi 
#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
	$serverPath/php/init.d/php74 stop
	rm -rf $serverPath/php/74
	echo "卸载php-${version}..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
