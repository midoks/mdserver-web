#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source

install_tmp=${rootPath}/tmp/mw_install.pl

Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-5.3.29 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-5.3.29.tar.xz ];then
	wget -O $sourcePath/php/php-5.3.29.tar.xz https://museum.php.net/php5/php-5.3.29.tar.xz
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

#
# --without-iconv=$serverPath/lib/libiconv \

#--enable-pcntl \
#--enable-bcmath \
#--enable-hash \
#--enable-libxml \
#--enable-dom \
#--enable-filter \
#--enable-fileinfo \
#--enable-xml \
#--enable-intl \
#--enable-exif \
#--enable-ftp \
#--enable-wddx \
#--enable-soap \
#--enable-posix \
# --with-zlib-dir=$serverPath/lib/zlib \
# --enable-zip \
cd $sourcePath/php/php-5.3.29 && ./configure \
--prefix=$serverPath/php/53 \
--exec-prefix=$serverPath/php/53 \
--with-config-file-path=$serverPath/php/53/etc \
--without-iconv \
--enable-sockets \
--enable-mbstring \
--enable-mysqlnd \
--enable-sysvmsg \
--enable-sysvsem \
--enable-sysvshm \
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
	echo "卸载php-5.3.29 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
