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
extFile=$serverPath/php/${version}/lib/php/extensions/no-debug-non-zts-20121212/swoole.so

Install_lib()
{

	isInstall=`cat $serverPath/php/$version/etc/php.ini|grep 'swoole.so'`
	if [ "${isInstall}" != "" ];then
		echo "php-$version 已安装yaf,请选择其它版本!"
		return
	fi
	
	if [ ! -f "$extFile" ];then
		
		wafV='1.10.1';
		if [ "$version" = '70' ] || [ "$version" = '71' ] || [ "$version" = '72' ];then
			wafV='2.2.0';
		fi

		php_lib=$sourcePath/php_${version}_lib
		mkdir -p $php_lib
		wget -O $php_lib/swoole-$wafV.tgz http://pecl.php.net/get/swoole-$wafV.tgz
		cd $php_lib
		tar xvf swoole-$wafV.tgz
		cd swoole-$wafV
		
		$serverPath/php/$version/bin/phpize
		./configure --with-php-config=$serverPath/php/$version/bin/php-config \
			--enable-openssl --with-openssl-dir=$serverPath/lib/openssl --enable-sockets
		make && make install
		cd ..
		rm -rf ${LIBNAME}-*
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

	echo "extension=$extFile"
	echo "extension=$extFile" >> $serverPath/php/$version/etc/php.ini
	
	$serverPath/php/init.d/php$version reload
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
		echo "php$version 未安装swoole,请选择其它版本!"
		return
	fi
	
	echo $serverPath/php/$version/etc/php.ini
	sed -i '_bak' "/swoole.so/d" $serverPath/php/$version/etc/php.ini
		
	rm -f $extFile
	$serverPath/php/init.d/php$version reload
	echo '==============================================='
	echo 'successful!'
}



if [ "$actionType" == 'install' ];then
	Install_lib
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_lib
fi