#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`
install_tmp=${rootPath}/tmp/mw_install.pl
SYS_ARCH=`arch`

version=5.2.17
PHP_VER=52
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

cd ${rootPath}/plugins/php/lib && /bin/bash zlib.sh

if [ ! -d $sourcePath/php/php${PHP_VER} ];then
	
	# ----------------------------------------------------------------------- #
	# 中国优化安装
	cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
	LOCAL_ADDR=common
	if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
		LOCAL_ADDR=cn
	fi

	if [ "$LOCAL_ADDR" == "cn" ];then
		if [ ! -f $sourcePath/php/php-${version}.tar.xz ];then
			wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.xz https://mirrors.sohu.com/php/php-${version}.tar.xz
		fi
	fi
	# ----------------------------------------------------------------------- #

	if [ ! -f $sourcePath/php/php-${version}.tar.gz ];then
		wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.gz https://museum.php.net/php5/php-${version}.tar.gz
	fi
	
	if [ ! -f $sourcePath/php/php-5.2.17-fpm-0.5.14.diff.gz ]; then
		wget --no-check-certificate -O $sourcePath/php/php-5.2.17-fpm-0.5.14.diff.gz http://php-fpm.org/downloads/php-5.2.17-fpm-0.5.14.diff.gz
	fi


	if [ ! -f $sourcePath/php/php-5.2.17-max-input-vars.patch ]; then
		wget --no-check-certificate -O $sourcePath/php/php-5.2.17-max-input-vars.patch https://raw.github.com/laruence/laruence.github.com/master/php-5.2-max-input-vars/php-5.2.17-max-input-vars.patch
	fi

	if [ ! -f $sourcePath/php/php-5.x.x.patch ]; then
		wget --no-check-certificate -O $sourcePath/php/php-5.x.x.patch https://mail.gnome.org/archives/xml/2012-August/txtbgxGXAvz4N.txt
	fi


	cd $sourcePath/php && tar -zxvf $sourcePath/php/php-${version}.tar.gz
	mv $sourcePath/php/php-${version} $sourcePath/php/php${PHP_VER}


	cd $sourcePath/php
	gzip -cd php-5.2.17-fpm-0.5.14.diff.gz | patch -d php${PHP_VER} -p1
	cd $sourcePath/php/php${PHP_VER}
	patch -p1 < ../php-5.2.17-max-input-vars.patch
	patch -p0 -b < ../php-5.x.x.patch 
	sed -i "s/\!png_check_sig (sig, 8)/png_sig_cmp (sig, 0, 8)/" ext/gd/libgd/gd_png.c
fi


if [  -f $serverPath/php/${PHP_VER}/bin/php.dSYM ];then
	mv $serverPath/php/${PHP_VER}/bin/php.dSYM $serverPath/php/${PHP_VER}/bin/php
fi

if [  -f $serverPath/php/${PHP_VER}/sbin/php-fpm.dSYM ];then
	mv $serverPath/php/${PHP_VER}/sbin/php-fpm.dSYM $serverPath/php/${PHP_VER}/sbin/php-fpm
fi


if [ -f $serverPath/php/${PHP_VER}/bin/php ];then
	return
fi

OPTIONS=''
if [ $sysName == 'Darwin' ]; then
	OPTIONS='--without-iconv'
	OPTIONS="${OPTIONS} --with-freetype-dir=${serverPath}/lib/freetype"
	OPTIONS="${OPTIONS} --with-curl=${serverPath}/lib/curl"
else
	OPTIONS='--without-iconv'
	# OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-curl"
fi


IS_64BIT=`getconf LONG_BIT`
if [ "$IS_64BIT" == "64" ];then
	OPTIONS="${OPTIONS} --with-libdir=lib64"
fi

if [ "${SYS_ARCH}" == "aarch64" ];then
	OPTIONS="$OPTIONS --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu"
fi


if [ ! -d $serverPath/php/${PHP_VER} ];then

	export MYSQL_LIB_DIR=/usr/lib64/mysql
	
	cd $sourcePath/php/php${PHP_VER} && ./configure \
	--prefix=$serverPath/php/${PHP_VER} \
	--exec-prefix=$serverPath/php/${PHP_VER} \
	--with-config-file-path=$serverPath/php/${PHP_VER}/etc \
	--with-zlib-dir=$serverPath/lib/zlib \
	--enable-zip \
	--enable-xml \
	--enable-shared \
	--with-mysql=mysqlnd \
	--enable-embedded-mysqli=shared \
	--enable-sysvmsg \
	--enable-sysvsem \
	--enable-sysvshm \
	$OPTIONS \
	--enable-fastcgi \
	--enable-fpm
	# ZEND_EXTRA_LIBS='-liconv'
	make && make install && make clean
fi

if [ "$?" != "0" ];then
	echo "install fail!!"
	rm -rf $sourcePath/php/php${PHP_VER}
	exit 2
fi


if [  -f $serverPath/php/${PHP_VER}/bin/php.dSYM ];then
	mv $serverPath/php/${PHP_VER}/bin/php.dSYM $serverPath/php/${PHP_VER}/bin/php
fi

if [  -f $serverPath/php/${PHP_VER}/sbin/php-fpm.dSYM ];then
	mv $serverPath/php/${PHP_VER}/sbin/php-fpm.dSYM $serverPath/php/${PHP_VER}/sbin/php-fpm
fi

if [ ! -d $serverPath/php/${PHP_VER}/lib/php/extensions/no-debug-non-zts-20060613 ]; then
	mkdir -p $serverPath/php/${PHP_VER}/lib/php/extensions/no-debug-non-zts-20060613
fi

# ps -ef|grep php/52 |grep -v grep |awk '{print $2}'|xargs kill
# /www/server/php/init.d/php52 start
# /www/server/php/52/sbin/php-fpm start
mkdir -p $serverPath/php/${PHP_VER}/var/log
mkdir -p $serverPath/php/${PHP_VER}/var/run

#------------------------ install end ------------------------------------#
}



Uninstall_php()
{
	$serverPath/php/init.d/php${PHP_VER} stop
	rm -rf $serverPath/php/${PHP_VER}
	echo "uninstall php-${version} ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
