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
actionType=$1
version=$2

LIBNAME=phalcon
LIBV=4.1.2

if [ "$version" -lt "73" ];then
	echo "not support!"
	exit 1
fi

if [ "$version" -gt "73" ];then
	LIBV=5.2.3
fi

LIB_PATH_NAME=lib/php
if [ -d $serverPath/rapira/${version}/lib64 ];then
	LIB_PATH_NAME=lib64
fi

NON_ZTS_FILENAME=`ls $serverPath/rapira/${version}/${LIB_PATH_NAME}/extensions | grep no-debug-non-zts`
extFile=$serverPath/rapira/${version}/${LIB_PATH_NAME}/extensions/${NON_ZTS_FILENAME}/${LIBNAME}.so

sysName=`uname`
if [ "$sysName" = "Darwin" ];then
	BAK='_bak'
else
	BAK=''
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

		php_lib=$sourcePath/php_lib
		mkdir -p $php_lib

		if [ ! -d $php_lib/${LIBNAME}-${LIBV} ];then
			if [ ! -f $php_lib/${LIBNAME}-${LIBV}.tgz ];then
				wget --no-check-certificate -O $php_lib/${LIBNAME}-${LIBV}.tgz http://pecl.php.net/get/${LIBNAME}-${LIBV}.tgz
			fi
			cd $php_lib && tar xvf ${LIBNAME}-${LIBV}.tgz
		fi
		cd $php_lib/${LIBNAME}-${LIBV}

		OPTIONS=''
		if [ "${SYS_ARCH}" = "aarch64" ] && [ "$version" -lt "56" ];then
			OPTIONS="$OPTIONS --build=aarch64-unknown-linux-gnu --host=aarch64-unknown-linux-gnu"
		fi
		
		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/rapira/$version/link/bin/php-config $OPTIONS
		make clean && make && make install && make clean

		cd $php_lib && rm -rf $php_lib/${LIBNAME}-${LIBV}
	fi
	
	while [[ ! -f "$extFile" ]];
    do
        echo -e ".\c"
        sleep 0.5
        if [ ! -f "$extFile" ];then
			echo "ERROR!"
		fi
        let n+=1
        if [ $n -gt 8 ];then
        	echo "WAIT " $n "TIMES FAIL!"
            return;
        fi
    done

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