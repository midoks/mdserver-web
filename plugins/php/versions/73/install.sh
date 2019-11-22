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


version=7.3.5
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-${version}.tar.xz ];then
	wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.xz http://au1.php.net/distributions/php-${version}.tar.xz
fi

if [ ! -d $sourcePath/php/php-${version} ];then
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-${version}.tar.xz
fi


OPTIONS=''
if [ $sysName == 'Darwin' ]; then
	OPTIONS='--without-iconv'
	OPTIONS="${OPTIONS} --with-curl=${serverPath}/lib/curl"
	OPTIONS="${OPTIONS} --enable-zip"
else
	OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-freetype-dir=${serverPath}/lib/freetype"
	OPTIONS="${OPTIONS} --with-gd --enable-gd-native-ttf"
	OPTIONS="${OPTIONS} --with-curl"
	OPTIONS="${OPTIONS} --with-libzip=${serverPath}/lib/libzip"
fi


# 
cd $sourcePath/php/php-${version} && ./configure \
--prefix=$serverPath/php/73 \
--exec-prefix=$serverPath/php/73 \
--with-config-file-path=$serverPath/php/73/etc \
--enable-mysqlnd \
--with-mysqli=mysqlnd \
--with-pdo-mysql=mysqlnd \
--enable-mbstring \
--with-zlib-dir=$serverPath/lib/zlib \
--enable-ftp \
--enable-sockets \
--enable-simplexml \
--enable-intl \
--enable-wddx \
--enable-soap \
--enable-posix \
--enable-sysvmsg \
--enable-sysvsem \
--enable-sysvshm \
$OPTIONS \
--enable-fpm \
&& make && make install && make clean

#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
	$serverPath/php/init.d/php73 stop
	rm -rf $serverPath/php/73
	echo "卸载php-${version}..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
