#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`

rapira_version=0.9.1
version=8.4
PHP_VER=84
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..."
mkdir -p $sourcePath/rapira
mkdir -p $serverPath/rapira


if [ ! -d $sourcePath/rapira/${PHP_VER} ];then

	if [ ! -f $sourcePath/rapira/rapira-${rapira_version}.tar.gz ];then
		wget --no-check-certificate -O $sourcePath/rapira/${rapira_version}.tar.gz https://github.com/rapira-rs/rapira/archive/refs/tags/v${rapira_version}.tar.gz
	fi
	
	cd $sourcePath/rapira && tar -zxvf $sourcePath/rapira/rapira-${rapira_version}.tar.gz
	mv $sourcePath/rapira/rapira-${rapira_version} $sourcePath/rapira/${PHP_VER}
fi

cd $sourcePath/rapira/${PHP_VER}

OPTIONS='--without-iconv'

# if [ $sysName = 'Darwin' ]; then
# 	OPTIONS="${OPTIONS} --with-curl"
# fi

argon_version=`pkg-config libargon2 --modversion`
if [ "$?" = "0" ];then
	OPTIONS="${OPTIONS} --with-password-argon2"
fi

IS_64BIT=`getconf LONG_BIT`
if [ "$IS_64BIT" = "64" ];then
	OPTIONS="${OPTIONS} --with-libdir=lib64"
fi

# ----- cpu start ------
if [ -z "${cpuCore}" ]; then
	cpuCore="1"
fi

if [ -f /proc/cpuinfo ];then
	cpuCore=`cat /proc/cpuinfo | grep "processor" | wc -l`
fi

MEM_INFO=$(which free > /dev/null && free -m|grep Mem|awk '{printf("%.f",($2)/1024)}')
if [ "${cpuCore}" != "1" ] && [ "${MEM_INFO}" != "0" ];then
    if [ "${cpuCore}" -gt "${MEM_INFO}" ];then
        cpuCore="${MEM_INFO}"
    fi
else
    cpuCore="1"
fi

if [ "$cpuCore" -gt "2" ];then
	cpuCore=`echo "$cpuCore" | awk '{printf("%.f",($1)*0.8)}'`
else
	cpuCore="1"
fi
# ----- cpu end ------

# OPTIONS="${OPTIONS} --enable-debug"
# OPTIONS="${OPTIONS} --enable-dtrace"

if [ "$sysName" = "Darwin" ];then
	BREW_DIR=`which brew`
	BREW_DIR=${BREW_DIR/\/bin\/brew/}

	LIB_DEPEND_DIR=`brew info openssl | grep ${BREW_DIR}/Cellar/openssl | cut -d \  -f 1 | awk 'END {print}'`
	OPTIONS="$OPTIONS --with-openssl=$(brew --prefix openssl)"
	export PKG_CONFIG_PATH=$LIB_DEPEND_DIR/lib/pkgconfig
	export OPENSSL_CFLAGS="-I${LIB_DEPEND_DIR}/include"
	export OPENSSL_LIBS="-L/${LIB_DEPEND_DIR}/lib -lssl -lcrypto -lz"
else
	# cd ${rootPath}/plugins/php/lib && /bin/bash openssl_35.sh
	# export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$serverPath/lib/openssl35/lib/pkgconfig
	OPTIONS="$OPTIONS --with-openssl"
fi

echo "$sourcePath/rapira/${PHP_VER}"

if [ ! -d $serverPath/rapira/${PHP_VER} ];then
	cd $sourcePath/rapira/${PHP_VER}
	# ./buildconf --force
	./configure \
	--prefix=$serverPath/rapira/${PHP_VER} \
	--exec-prefix=$serverPath/rapira/${PHP_VER} \
	--with-config-file-path=$serverPath/rapira/${PHP_VER}/etc \
	--enable-mysqlnd \
	--with-mysql=mysqlnd \
	--with-mysqli=mysqlnd \
	--with-pdo-mysql=mysqlnd \
	--with-mysqlnd-ssl \
	--enable-mbstring \
	--enable-ftp \
	--enable-sockets \
	--enable-simplexml \
	--enable-soap \
	--enable-posix \
	--enable-sysvmsg \
	--enable-sysvsem \
	--enable-sysvshm \
	--disable-intl \
	--disable-fileinfo \
	$OPTIONS \
	--enable-fpm
	make clean && make -j${cpuCore} && make install && make clean

	# rm -rf $sourcePath/php/php${PHP_VER}
fi 
#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
	$serverPath/php/init.d/php${PHP_VER} stop
	rm -rf $serverPath/php/${PHP_VER}
	echo "卸载php-${version}..."
}

action=${1}
if [ "${1}" = 'install' ];then
	Install_php
else
	Uninstall_php
fi
