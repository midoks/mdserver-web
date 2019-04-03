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
echo "安装php-7.0.30 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-7.0.30.tar.xz ];then
	wget -O $sourcePath/php/php-7.0.30.tar.xz https://museum.php.net/php7/php-7.0.30.tar.xz
fi

if [ ! -d $sourcePath/php/php-7.0.30 ];then
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-7.0.30.tar.xz
fi

OPTIONS=''
if [ $sysName == 'Darwin' ]; then
	OPTIONS='--without-iconv'
	OPTIONS="${OPTIONS} --with-curl=${serverPath}/lib/curl"
else
	OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-gd --enable-gd-native-ttf"
	OPTIONS="${OPTIONS} --with-curl"
fi


cd $sourcePath/php/php-7.0.30 && ./configure \
--prefix=$serverPath/php/70 \
--exec-prefix=$serverPath/php/70 \
--with-config-file-path=$serverPath/php/70/etc \
--with-zlib-dir=$serverPath/lib/zlib \
--enable-mysqlnd \
--with-mysqli=mysqlnd \
--with-pdo-mysql=mysqlnd \
--enable-zip \
--enable-mbstring \
--enable-simplexml \
--enable-ftp \
--enable-sockets \
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
	$serverPath/php/init.d/php70 stop
	rm -rf $serverPath/php/70
	echo "卸载php-7.0.30 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
