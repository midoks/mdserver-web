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


version=5.4.45
PHP_VER=54
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php


cd ${rootPath}/plugins/php/lib && /bin/bash zlib.sh

if [ ! -d $sourcePath/php/php${PHP_VER} ];then
	if [ ! -f $sourcePath/php/php-${version}.tar.gz ];then
		wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.gz https://museum.php.net/php5/php-${version}.tar.gz
	fi
	
	cd $sourcePath/php && tar -zxvf $sourcePath/php/php-${version}.tar.gz
	mv $sourcePath/php/php-${version} $sourcePath/php/php${PHP_VER}
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


if [ ! -d $serverPath/php/${PHP_VER} ];then
	cd $sourcePath/php/php${PHP_VER} && ./configure \
	--prefix=$serverPath/php/${PHP_VER} \
	--exec-prefix=$serverPath/php/${PHP_VER} \
	--with-config-file-path=$serverPath/php/${PHP_VER}/etc \
	--with-zlib-dir=$serverPath/lib/zlib \
	--enable-mysqlnd \
	--with-mysql=mysqlnd \
	--with-pdo-mysql=mysqlnd \
	--with-mysqli=mysqlnd \
	--enable-zip \
	--enable-mbstring \
	--enable-sockets \
	--enable-ftp \
	--enable-simplexml \
	--enable-soap \
	--enable-posix \
	--enable-sysvmsg \
	--enable-sysvsem \
	--enable-sysvshm \
	--disable-fileinfo \
	$OPTIONS \
	--enable-fpm

	make clean && make -j${cpuCore}

	#debian11,没有生成php54 man
	if [ ! -f sapi/cli/php.1 ];then
		cp -rf sapi/cli/php.1.in sapi/cli/php.1
	fi

	if [ ! -f sapi/cgi/php-cgi.1 ];then
		cp -rf sapi/cgi/php-cgi.1.in sapi/cgi/php-cgi.1
	fi

	if [ ! -f scripts/man1/phpize.1 ];then
		cp -rf scripts/man1/phpize.1.in scripts/man1/phpize.1
	fi

	if [ ! -f scripts/man1/php-config.1 ];then
		cp -rf scripts/man1/php-config.1.in scripts/man1/php-config.1
	fi

	if [ ! -f ext/phar/phar.1 ];then
		cp -rf ext/phar/phar.1.in ext/phar/phar.1
	fi

	if [ ! -f ext/phar/phar.phar.1 ];then
		cp -rf ext/phar/phar.phar.1.in ext/phar/phar.phar.1
	fi


	make install && make clean
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
