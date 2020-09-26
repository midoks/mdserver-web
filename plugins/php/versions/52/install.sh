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


version=5.2.17
PHP_VER=52
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -d $sourcePath/php/php${PHP_VER} ];then
	if [ ! -f $sourcePath/php/php-${version}.tar.gz ];then
		wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.gz https://museum.php.net/php5/php-${PHP_VER}.tar.gz
	fi
	
	if [ ! -f $sourcePath/php/php-5.2.17-fpm-0.5.14.diff.gz ]; then
		wget -O $sourcePath/php/php-5.2.17-fpm-0.5.14.diff.gz http://php-fpm.org/downloads/php-5.2.17-fpm-0.5.14.diff.gz
	fi


	if [ ! -f $sourcePath/php/php-5.2.17-max-input-vars.patch ]; then
		wget -O $sourcePath/php/php-5.2.17-max-input-vars.patch https://raw.github.com/laruence/laruence.github.com/master/php-5.2-max-input-vars/php-5.2.17-max-input-vars.patch
	fi


	cd $sourcePath/php && tar -zxvf $sourcePath/php/php-${version}.tar.gz
	mv $sourcePath/php/php-${version} $sourcePath/php/php${PHP_VER}


	cd $sourcePath/php
	gzip -cd php-5.2.17-fpm-0.5.14.diff.gz | patch -d php${PHP_VER} -p1
	cd $sourcePath/php/php${PHP_VER}
	patch -p1 < ../php-5.2.17-max-input-vars.patch
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
	OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-freetype-dir=${serverPath}/lib/freetype"
	OPTIONS="${OPTIONS} --with-gd --enable-gd-native-ttf"
	OPTIONS="${OPTIONS} --with-curl"
fi

\cp -rf ${curPath}/lib/node.c $sourcePath/php/php${PHP_VER}/ext/dom/node.c
\cp -rf ${curPath}/lib/documenttype.c $sourcePath/php/php${PHP_VER}/ext/dom/documenttype.c


if [ ! -d $serverPath/php/${PHP_VER} ];then
	ln -s /usr/lib64/libjpeg.so /usr/lib/libjpeg.so
	ln -s /usr/lib64/libpng.so /usr/lib/

	cd $sourcePath/php/php${PHP_VER} && ./configure \
	--prefix=$serverPath/php/${PHP_VER} \
	--exec-prefix=$serverPath/php/${PHP_VER} \
	--with-config-file-path=$serverPath/php/${PHP_VER}/etc \
	--enable-sysvmsg \
	--enable-sysvsem \
	--enable-sysvshm \
	$OPTIONS \
	--enable-fastcgi \
	--enable-fpm \
	&& make && make install && make clean
fi

if [ "$?" != "0" ];then
	echo "install fail!!"
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
