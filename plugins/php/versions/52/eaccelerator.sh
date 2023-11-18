#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# php 5.2.17 + eaccelerator 0.9.5.3
# php 5.3.24 + eaccelerator 0.9.6.1
# php 5.4.14 + eaccelerator 1.0 dev


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

LIBNAME=eaccelerator
LIBV=0.9.6
sysName=`uname`
actionType=$1
version=$2


NON_ZTS_FILENAME=`ls $serverPath/php/${version}/lib/php/extensions | grep no-debug-non-zts`
extFile=$serverPath/php/${version}/lib/php/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

Install_lib()
{
	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib

		if [ ! -d $php_lib/${LIBNAME}-${LIBV} ];then
			wget -O $php_lib/${LIBNAME}-${LIBV}.tar.gz https://github.com/eaccelerator/eaccelerator/archive/${LIBV}.tar.gz
			# wget -O $php_lib/${LIBNAME}-${LIBV}.tar.bz2 http://dl.wdlinux.cn:5180/soft/eaccelerator-0.9.6.1.tar.bz2
			cd $php_lib && tar -zxvf ${LIBNAME}-${LIBV}.tar.gz
		fi
		cd $php_lib/${LIBNAME}-${LIBV}

		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config \
		--enable-eaccelerator=shared
		make && make install && make clean

	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return
	fi

	EA_DIR=/tmp/eaccelerator
	mkdir -p $EA_DIR
	chmod 777 -R $EA_DIR
	echo "" >> $serverPath/php/$version/etc/php.ini
	echo "[${LIBNAME}]" >> $serverPath/php/$version/etc/php.ini
	echo "extension=${LIBNAME}.so" >> $serverPath/php/$version/etc/php.ini
	echo "${LIBNAME}.enable=1" >> $serverPath/php/$version/etc/php.ini
	echo "${LIBNAME}.optimizer=1" >> $serverPath/php/$version/etc/php.ini
	echo "${LIBNAME}.shm_size=64" >> $serverPath/php/$version/etc/php.ini
	echo "${LIBNAME}.cache_dir=${EA_DIR}" >> $serverPath/php/$version/etc/php.ini
	echo "${LIBNAME}.allowed_admin_path=/www/wwwroot/you_project_dir" >> $serverPath/php/$version/etc/php.ini



	bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "$serverPath/php/$version/bin/php-config" ];then
		echo "php$version 未安装,请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then
		echo "php$version 未安装${LIBNAME},请选择其它版本!"
		echo "php-$vphp not install ${LIBNAME}, Plese select other version!"
		return
	fi
	
	sed -i $BAK "/${LIBNAME}.so/d" $serverPath/php/$version/etc/php.ini
	sed -i $BAK "/${LIBNAME}/d" $serverPath/php/$version/etc/php.ini
		
	rm -f $extFile

	bash ${rootPath}/plugins/php/versions/lib.sh $version restart
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi