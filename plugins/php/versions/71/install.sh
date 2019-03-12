#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source

install_tmp=${rootPath}/tmp/mw_install.pl

# echo $curPath
# echo ${1}
# echo ${serverPath}
# echo ${install_tmp}

version=7.1.27
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-${version}.tar.xz ];then
	wget -O $sourcePath/php/php-${version}.tar.xz http://au1.php.net/distributions/php-${version}.tar.xz
fi

if [ ! -d $sourcePath/php/php-${version} ];then
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-${version}.tar.xz
fi


cd $sourcePath/php/php-${version} && ./configure \
--prefix=$serverPath/php/71 \
--exec-prefix=$serverPath/php/71 \
--with-config-file-path=$serverPath/php/71/etc \
--with-zlib-dir=$serverPath/lib/zlib \
--enable-mysqlnd \
--without-iconv \
--enable-zip \
--enable-mbstring \
--enable-ftp \
--enable-wddx \
--enable-sockets \
--enable-intl \
--enable-soap \
--enable-posix \
--enable-sysvmsg \
--enable-sysvsem \
--enable-sysvshm \
--enable-fpm \
&& make && make install && make clean

#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
	$serverPath/php/init.d/php71 stop
	rm -rf $serverPath/php/71
	echo "卸载php-${version}..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
