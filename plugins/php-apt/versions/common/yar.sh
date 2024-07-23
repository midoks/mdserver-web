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
LIBNAME=yar
LIBV=2.3.3

if [[  "$version" =~ "5.0" ]];then
	LIBV=1.2.5
fi

if [[  "$version" =~ "7.0" ]];then
	LIBV=2.3.3
fi

extVer=`bash $curPath/lib.sh $version`
extFile=/usr/lib/php/${extVer}/${LIBNAME}.so



if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

Install_lib()
{

	#cat /etc/php/${version}/fpm/conf.d/* | grep -v '^;' |tr -s '\n'
	isInstall=`cat /etc/php/${version}/fpm/conf.d/* | grep -v '^;' |tr -s '\n' |grep "${LIBNAME}.so"`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装${LIBNAME},请选择其它版本!"
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

		/usr/bin/phpize${version}
		./configure --with-php-config=/usr/bin/php-config${version}
		make && make install && make clean

	fi
	echo "$extFile checking ..."
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return;
	fi

	
	echo  "" >> /etc/php/${version}/fpm/conf.d/${LIBNAME}.ini
	echo  "[${LIBNAME}]" >> /etc/php/${version}/fpm/conf.d/${LIBNAME}.ini
	echo  "extension=${LIBNAME}.so" >> /etc/php/${version}/fpm/conf.d/${LIBNAME}.ini
	echo  "${LIBNAME}.expose_info=false" >>  /etc/php/${version}/fpm/conf.d/${LIBNAME}.ini
	
	systemctl restart php${version}-fpm 
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_lib()
{
	if [ ! -f "/usr/bin/php-config${version}" ];then
		echo "php-$version 未安装,请选择其它版本!"
		return
	fi

	
	if [ -f /etc/php/${version}/fpm/conf.d/${LIBNAME}.ini ];then
		rm -rf /etc/php/${version}/fpm/conf.d/${LIBNAME}.ini
		rm -rf $extFile
	fi

	systemctl restart php${version}-fpm 
	echo '==============================================='
	echo 'successful!'
}


if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi