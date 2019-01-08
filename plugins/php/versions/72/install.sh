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
echo "安装php-7.2.5 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-7.2.5.tar.xz ];then
	wget -O $sourcePath/php/php-7.2.5.tar.xz https://museum.php.net/php7/php-7.2.5.tar.xz
fi

if [ ! -d $sourcePath/php/php-7.2.5 ];then
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-7.2.5.tar.xz
fi


cd $sourcePath/php/php-7.2.5 && ./configure \
--prefix=$serverPath/php/72 \
--exec-prefix=$serverPath/php/72 \
--with-config-file-path=$serverPath/php/72/etc \
--with-zlib-dir=$serverPath/lib/zlib \
--enable-mysqlnd \
--without-iconv \
--enable-zip \
--enable-mbstring \
--enable-ftp \
--enable-wddx \
--enable-soap \
--enable-posix \
--enable-fpm \
&& make && make install && make clean

#------------------------ install end ------------------------------------#
}



Uninstall_php()
{
	rm -rf $serverPath/php/72
	echo "卸载php-7.2.5 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
