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

function version_gt() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" != "$1"; }
function version_le() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" == "$1"; }
function version_lt() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" != "$1"; }
function version_ge() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" == "$1"; }


version=8.0.30
PHP_VER=80
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装php-${version} ..." > $install_tmp
mkdir -p $sourcePath/php
mkdir -p $serverPath/php

cd ${rootPath}/plugins/php/lib && /bin/bash freetype_new.sh
cd ${rootPath}/plugins/php/lib && /bin/bash zlib.sh

# redat ge 8
which yum
if [ "$?" == "0" ];then
	cd ${rootPath}/plugins/php/lib && /bin/bash oniguruma.sh
fi

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

	if [ ! -f $sourcePath/php/php-${version}.tar.xz ];then
		wget --no-check-certificate -O $sourcePath/php/php-${version}.tar.xz https://www.php.net/distributions/php-${version}.tar.xz
	fi

	#检测文件是否损坏.
	md5_file_ok=216ab305737a5d392107112d618a755dc5df42058226f1670e9db90e77d777d9
	if [ -f $sourcePath/php/php-${version}.tar.xz ];then
		md5_file=`sha256sum $sourcePath/php/php-${version}.tar.xz  | awk '{print $1}'`
		if [ "${md5_file}" != "${md5_file_ok}" ]; then
			echo "PHP${version} 下载文件不完整,重新安装"
			rm -rf $sourcePath/php/php-${version}.tar.xz
		fi
	fi
	
	cd $sourcePath/php && tar -Jxf $sourcePath/php/php-${version}.tar.xz
	mv $sourcePath/php/php-${version} $sourcePath/php/php${PHP_VER}
fi

cd $sourcePath/php/php${PHP_VER}

OPTIONS='--without-iconv'
if [ $sysName == 'Darwin' ]; then
	OPTIONS="${OPTIONS} --with-curl"
	OPTIONS="${OPTIONS} --with-external-pcre=$(brew --prefix pcre2)"
else
	# OPTIONS="--with-iconv=${serverPath}/lib/libiconv"
	OPTIONS="${OPTIONS} --with-curl"
	OPTIONS="${OPTIONS} --with-readline"
fi

IS_64BIT=`getconf LONG_BIT`
if [ "$IS_64BIT" == "64" ];then
	OPTIONS="${OPTIONS} --with-libdir=lib64"
fi


# argon_version=`pkg-config libargon2 --modversion`
# if [ "$?" == "0" ];then
# 	OPTIONS="${OPTIONS} --with-password-argon2"
# fi


ZIP_OPTION='--with-zip'
libzip_version=`pkg-config libzip --modversion`
if version_lt "$libzip_version" "0.11.0" ;then
	cd ${rootPath}/plugins/php/lib && /bin/bash libzip.sh
	export PKG_CONFIG_PATH=$serverPath/lib/libzip/lib/pkgconfig
	ZIP_OPTION="--with-zip=$serverPath/lib/libzip"
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

if [ "$cpuCore" -gt "2" ];then
	cpuCore=`echo "$cpuCore" | awk '{printf("%.f",($1)*0.8)}'`
else
	cpuCore="1"
fi
# ----- cpu end ------

echo "$sourcePath/php/php${PHP_VER}"

if [ ! -d $serverPath/php/${PHP_VER} ];then
	cd $sourcePath/php/php${PHP_VER}
	./buildconf --force
	./configure \
	--prefix=$serverPath/php/${PHP_VER} \
	--exec-prefix=$serverPath/php/${PHP_VER} \
	--with-config-file-path=$serverPath/php/${PHP_VER}/etc \
	--enable-mysqlnd \
	--with-mysqli=mysqlnd \
	--with-pdo-mysql=mysqlnd \
	--with-zlib-dir=$serverPath/lib/zlib \
	$ZIP_OPTION \
	--enable-ftp \
	--enable-mbstring \
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
	echo "卸载php-${version}..." > $install_tmp
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_php
else
	Uninstall_php
fi
