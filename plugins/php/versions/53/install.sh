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



version=5.3.29
PHP_VER=53
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-5.3.29 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

cd ${rootPath}/plugins/php/lib && /bin/bash zlib.sh

if [ ! -d $sourcePath/php/php${PHP_VER} ];then
	if [ ! -f $sourcePath/php/php-${version}.tar.xz ];then
		wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.xz https://museum.php.net/php5/php-${version}.tar.xz
	fi
	
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-${version}.tar.xz
	mv $sourcePath/php/php-${version} $sourcePath/php/php${PHP_VER}
fi


if [ -f $serverPath/php/53/bin/php ];then
	return
fi

# OPTIONS="${OPTIONS} --with-freetype-dir=${serverPath}/lib/freetype_old"
# OPTIONS="${OPTIONS} --with-gd --enable-gd-native-ttf"
# OPTIONS="${OPTIONS} --with-jpeg --with-jpeg-dir=/usr/lib"
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

# ----- cpu start ------
if [ -z "${cpuCore}" ]; then
	cpuCore="1"
fi

if [ -f /proc/cpuinfo ];then
	cpuCore=`cat /proc/cpuinfo | grep "processor" | wc -l`
fi

MEM_INFO=$(free -m|grep Mem|awk '{printf("%.f",($2)/1024)}')
if [ "${cpuCore}" != "1" ] && [ "${MEM_INFO}" != "0" ];then
    if [ "${cpuCore}" -gt "${MEM_INFO}" ];then
        cpuCore="${MEM_INFO}"
    fi
else
    cpuCore="1"
fi

if [ "$cpuCore" -gt "1" ];then
	cpuCore=`echo "$cpuCore" | awk '{printf("%.f",($1)*0.8)}'`
fi
# ----- cpu end ------

if [ ! -d $serverPath/php/53/bin ];then
	cd $sourcePath/php/php${PHP_VER} && ./configure \
	--prefix=$serverPath/php/53 \
	--exec-prefix=$serverPath/php/53 \
	--with-config-file-path=$serverPath/php/53/etc \
	--with-zlib-dir=$serverPath/lib/zlib \
	--enable-mysqlnd \
	--with-mysql=mysqlnd \
	--with-pdo-mysql=mysqlnd \
	--with-mysqli=mysqlnd \
	--enable-zip \
	--enable-exif \
	--enable-hash \
	--enable-libxml \
	--enable-simplexml \
	--enable-dom \
	--enable-filter \
	--enable-pcntl \
	--enable-bcmath \
	--enable-xml \
	--enable-ftp \
	--enable-soap \
	--enable-posix \
	--enable-sockets \
	--enable-mbstring \
	--enable-sysvmsg \
	--enable-sysvsem \
	--enable-sysvshm \
	--disable-fileinfo \
	$OPTIONS \
	--enable-fpm
	make clean && make -j${cpuCore} && make install && make clean
fi


if [  -f $serverPath/php/53/bin/php.dSYM ];then
	mv $serverPath/php/53/bin/php.dSYM $serverPath/php/53/bin/php
fi

if [  -f $serverPath/php/53/sbin/php-fpm.dSYM ];then
	mv $serverPath/php/53/sbin/php-fpm.dSYM $serverPath/php/53/sbin/php-fpm
fi


if [ -d $serverPath/php/53 ] && [ ! -d $serverPath/php/53/lib/php/extensions/no-debug-non-zts-20090626 ]; then
	mkdir -p $serverPath/php/53/lib/php/extensions/no-debug-non-zts-20090626
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
