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
echo "安装php-5.2.17 ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

if [ ! -f $sourcePath/php/php-5.2.17.tar.bz2 ];then
	wget -O $sourcePath/php/php-5.2.17.tar.bz2 https://museum.php.net/php5/php-5.2.17.tar.bz2
fi

if [ ! -d $sourcePath/php/php-5.2.17 ];then
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-5.2.17.tar.bz2
fi


cd $sourcePath/php/php-5.2.17 && ./configure \
--prefix=$serverPath/php/php52 \
--exec-prefix=$serverPath/php/php52 \
--with-config-file-path=$serverPath/php/php55/etc \
--with-zlib-dir=$serverPath/lib/zlib \
--without-iconv \
--enable-zip \
--enable-mbstring \
--enable-ftp \
--enable-wddx \
--enable-soap \
--enable-posix \
--enable-fpm \
&& make && make install

#------------------------ install end ------------------------------------#
}



Uninstall_php()
{
	echo "卸载php-5.2.17 ..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
