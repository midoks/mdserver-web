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



Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-5.4.45 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-5.4.45.tar.gz ];then
	wget --no-check-certificate -O $sourcePath/php/php-5.4.45.tar.gz https://museum.php.net/php5/php-5.4.45.tar.gz
fi

if [ ! -d $sourcePath/php/php-5.4.45 ];then
	cd $sourcePath/php && tar -zvxf $sourcePath/php/php-5.4.45.tar.gz
fi


OPTIONS=''
if [ $sysName == 'Darwin' ]; then
	OPTIONS='--without-iconv'
	OPTIONS="${OPTIONS} --with-freetype-dir=${serverPath}/lib/freetype"
	OPTIONS="${OPTIONS} --with-curl=${serverPath}/lib/curl"
else
	OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-freetype-dir=${serverPath}/lib/freetype"
	OPTIONS="${OPTIONS} --with-gd --enable-gd-native-ttf"
	OPTIONS="${OPTIONS} --with-curl"
fi

if [ ! -d $serverPath/php/54 ];then
	cd $sourcePath/php/php-5.4.45 && ./configure \
	--prefix=$serverPath/php/54 \
	--exec-prefix=$serverPath/php/54 \
	--with-config-file-path=$serverPath/php/54/etc \
	--with-zlib-dir=$serverPath/lib/zlib \
	--enable-mysqlnd \
	--enable-zip \
	--enable-mbstring \
	--enable-sockets \
	--enable-ftp \
	--enable-simplexml \
	--enable-wddx \
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
	$serverPath/php/init.d/php54 stop
	rm -rf $serverPath/php/54
	echo "卸载php-5.4.45 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
