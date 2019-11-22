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
echo "安装php-5.3.29 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-5.3.29.tar.xz ];then
	wget --no-check-certificate -O $sourcePath/php/php-5.3.29.tar.xz https://museum.php.net/php5/php-5.3.29.tar.xz
fi

if [ ! -d $sourcePath/php/php-5.3.29 ];then
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-5.3.29.tar.xz
fi



if [  -f $serverPath/php/53/bin/php.dSYM ];then
	mv $serverPath/php/53/bin/php.dSYM $serverPath/php/53/bin/php
fi

if [  -f $serverPath/php/53/sbin/php-fpm.dSYM ];then
	mv $serverPath/php/53/sbin/php-fpm.dSYM $serverPath/php/53/sbin/php-fpm
fi


if [ -f $serverPath/php/53/bin/php ];then
	return
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

# --enable-intl \
cd $sourcePath/php/php-5.3.29 && ./configure \
--prefix=$serverPath/php/53 \
--exec-prefix=$serverPath/php/53 \
--with-config-file-path=$serverPath/php/53/etc \
--with-zlib-dir=$serverPath/lib/zlib \
--enable-zip \
--enable-exif \
--enable-hash \
--enable-libxml \
--enable-simplexml \
--enable-dom \
--enable-filter \
--enable-fileinfo \
--enable-pcntl \
--enable-bcmath \
--enable-xml \
--enable-ftp \
--enable-wddx \
--enable-soap \
--enable-posix \
--enable-sockets \
--enable-mbstring \
--enable-mysqlnd \
--enable-sysvmsg \
--enable-sysvsem \
--enable-sysvshm \
$OPTIONS \
--enable-fpm \
&& make && make install && make clean


if [  -f $serverPath/php/53/bin/php.dSYM ];then
	mv $serverPath/php/53/bin/php.dSYM $serverPath/php/53/bin/php
fi

if [  -f $serverPath/php/53/sbin/php-fpm.dSYM ];then
	mv $serverPath/php/53/sbin/php-fpm.dSYM $serverPath/php/53/sbin/php-fpm
fi

#------------------------ install end ------------------------------------#
}



Uninstall_php()
{
	$serverPath/php/init.d/php53 stop
	rm -rf $serverPath/php/53
	echo "uninstall php-5.3.29 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
