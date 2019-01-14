#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source

install_tmp=${rootPath}/tmp/bt_install.pl

# echo $curPath
# echo ${1}
# echo ${serverPath}
# echo ${install_tmp}


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


cd $sourcePath/php/php-5.6.36 && ./configure \
--prefix=$serverPath/php/56 \
--exec-prefix=$serverPath/php/56 \
--with-config-file-path=$serverPath/php/56/etc \
--with-zlib-dir=$serverPath/lib/zlib \
--with-mysql \
--with-mysqli \
--without-iconv \
--enable-zip \
--enable-mbstring \
--enable-ftp \
--enable-wddx \
--enable-soap \
--enable-posix \
--enable-fpm \
--enable-sockets \
&& make && make install && make clean

#------------------------ install end ------------------------------------#
}



Uninstall_php()
{
	echo "卸载php-5.6.36 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
