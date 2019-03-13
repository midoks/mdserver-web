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
echo "安装php-5.6.36 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-5.6.36.tar.xz ];then
	wget -O $sourcePath/php/php-5.6.36.tar.xz https://museum.php.net/php5/php-5.6.36.tar.xz
fi

if [ ! -d $sourcePath/php/php-5.6.36 ];then
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-5.6.36.tar.xz
fi

OPTIONS=''
if [ $sysName == 'Darwin' ]; then
	OPTIONS='--without-iconv'
else
	OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-gd --enable-gd-native-ttf"
fi

cd $sourcePath/php/php-5.6.36 && ./configure \
--prefix=$serverPath/php/56 \
--exec-prefix=$serverPath/php/56 \
--with-config-file-path=$serverPath/php/56/etc \
--with-zlib-dir=$serverPath/lib/zlib \
--with-mysql=mysqlnd \
--with-pdo-mysql=mysqlnd \
--with-mysqli=mysqlnd \
--enable-zip \
--enable-mbstring \
--enable-simplexml \
--enable-intl \
--enable-ftp \
--enable-sockets \
--enable-pcntl \
--enable-shmop \
--enable-intl \
--enable-wddx \
--enable-soap \
--enable-posix \
--enable-sysvmsg \
--enable-sysvsem \
--enable-sysvshm \
$OPTIONS \
--enable-fpm \
&& make clean && make && make install && make clean

#------------------------ install end ------------------------------------#
}



Uninstall_php()
{
	$serverPath/php/init.d/php56 stop
	rm -rf $serverPath/php/56
	echo "卸载php-5.6.36 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
