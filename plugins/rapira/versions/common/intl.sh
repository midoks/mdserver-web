#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`

rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/rapira

SYS_ARCH=`arch`

# _os=`uname`

# if [ ${_os} = "Darwin" ]; then
# 	OSNAME='macos'
# elif grep -Eq "openSUSE" /etc/*-release; then
# 	OSNAME='opensuse'
# elif grep -Eq "FreeBSD" /etc/*-release; then
# 	OSNAME='freebsd'
# elif grep -Eqi "CentOS" /etc/issue || grep -Eqi "CentOS" /etc/*-release; then
# 	OSNAME='rhel'
# elif grep -Eqi "Fedora" /etc/issue || grep -Eqi "Fedora" /etc/*-release; then
# 	OSNAME='rhel'
# elif grep -Eqi "Rocky" /etc/issue || grep -Eqi "Rocky" /etc/*-release; then
# 	OSNAME='rhel'
# elif grep -Eqi "AlmaLinux" /etc/issue || grep -Eqi "AlmaLinux" /etc/*-release; then
# 	OSNAME='rhel'
# elif grep -Eqi "Amazon Linux" /etc/issue || grep -Eqi "Amazon Linux" /etc/*-release; then
# 	OSNAME='amazon'
# elif grep -Eqi "Debian" /etc/issue || grep -Eqi "Debian" /etc/*-release; then
# 	OSNAME='debian'
# elif grep -Eqi "Ubuntu" /etc/issue || grep -Eqi "Ubuntu" /etc/*-release; then
# 	OSNAME='ubuntu'
# else
# 	OSNAME='unknow'
# fi

actionType=$1
version=$2


LIBNAME=intl
LIBV=0

LIB_PATH_NAME=lib/php
if [ -d $serverPath/rapira/${version}/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/rapira/${version}/link/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/rapira/${version}/link/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

sysName=`uname`
if [ "$sysName" = "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

OPTIONS=''
if [ "$version" -lt "74" ];then

	# cd /www/server/mdserver-web/plugins/rapira/lib && /bin/bash icu.sh
	cd ${rootPath}/plugins/rapira/lib && /bin/bash icu.sh
	OPTIONS="--with-icu-dir=${serverPath}/lib/icu"
fi

phpini=$serverPath/rapira/$version/php.ini

Install_lib()
{

	isInstall=`cat ${phpini}|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then

		if [ ! -d $sourcePath/php${version}/ext ];then
			cd ${rootPath}/plugins/rapira && /bin/bash ${rootPath}/plugins/rapira/versions/${version}/install.sh install 
		fi

		cd $sourcePath/php${version}/ext/${LIBNAME}
		if [ "${SYS_ARCH}" = "aarch64" ] && [ "$version" -lt "56" ];then
			OPTIONS="$OPTIONS --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu"
		fi

		if [ "$sysName" = "Darwin" ];then
			LIB_DEPEND_DIR=`brew --prefix icu4c`
			export PKG_CONFIG_PATH="${LIB_DEPEND_DIR}/lib/pkgconfig"
			OPTIONS="$OPTIONS --with-icu-dir=$LIB_DEPEND_DIR"
			OPTIONS="$OPTIONS --enable-intl"
		fi		


		$serverPath/rapira/$version/link/bin/phpize
		./configure --with-php-config=$serverPath/rapira/$version/link/bin/php-config $OPTIONS
		make clean && make && make install && make clean
		
		if [ -d $sourcePath/php${version} ];then
			cd ${sourcePath} && rm -rf $sourcePath/php${version}
		fi
	fi

	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi


    echo "" >> $phpini
	echo "[${LIBNAME}]" >> $phpini
	echo "extension=${LIBNAME}.so" >> $phpini
	
	cd  ${curPath} && bash ${rootPath}/plugins/rapira/versions/lib.sh $version restart
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "$serverPath/rapira/$version/link/bin/php-config" ];then
		echo "php-$version 未安装,请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then
		echo "php-$version 未安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	sed -i $BAK "/${LIBNAME}.so/d" $phpini
	sed -i $BAK "/${LIBNAME}/d" $phpini
		
	rm -f $extFile
	cd  ${curPath} && bash ${rootPath}/plugins/rapira/versions/lib.sh $version restart
	echo '==============================================='
	echo 'successful!'
}



if [ "$actionType" = 'install' ];then
	Install_lib
elif [ "$actionType" = 'uninstall' ];then
	Uninstall_lib
fi