#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

actionType=$1
version=$2

sysName=`uname`
LIBNAME=yaf
LIBV=3.3.6

cfgDir=/etc/opt/remi

if [ `echo "$version < 7.0"|bc` -eq 1 ];then
	LIBV=2.3.5
fi

extVer=`bash $curPath/lib.sh $version`
extFile=/usr/lib/php/${extVer}/${LIBNAME}.so

ext_dir=${cfgDir}/php${version}/php.d
ext_file=${ext_dir}/30-yaf.ini

Install_lib()
{

	isInstall=`cat ${cfgDir}/php/${version}/php.d/* | grep -v '^;' |tr -s '\n' |grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-yum-$version 已安装${LIBNAME},请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib
		if [ ! -d $php_lib/${LIBNAME}-${LIBV} ];then
			wget -O $php_lib/${LIBNAME}-${LIBV}.tgz http://pecl.php.net/get/${LIBNAME}-${LIBV}.tgz
			cd $php_lib && tar xvf ${LIBNAME}-${LIBV}.tgz
		fi 
		cd $php_lib/${LIBNAME}-${LIBV}

		/opt/remi/php${version}/root/usr/bin/phpize
		./configure
		make && make install && make clean

	fi
	echo "$extFile checking ..."
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return;
	fi

	
	echo  "" >> $ext_file
	echo  "[${LIBNAME}]" >> $ext_file
	echo  "extension=${LIBNAME}.so" >> $ext_file
	
	systemctl restart php${version}-php-fpm
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "/usr/bin/php-config${version}" ];then
		echo "php-$version 未安装,请选择其它版本!"
		return
	fi
	
	if [ -f $ext_file ];then
		rm -rf $ext_file
	fi

	systemctl restart php${version}-php-fpm
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi