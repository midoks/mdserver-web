#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`

rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
echo $serverPath
Install_yaf()
{
	case "${version}" in 
		'54')
		extFile='/www/server/php/54/lib/php/extensions/no-debug-non-zts-20100525/yaf.so'
		;;
		'55')
		extFile='/www/server/php/55/lib/php/extensions/no-debug-non-zts-20121212/yaf.so'
		;;
		'56')
		extFile='/www/server/php/56/lib/php/extensions/no-debug-non-zts-20131226/yaf.so'
		;;
		'70')
		extFile='/www/server/php/70/lib/php/extensions/no-debug-non-zts-20151012/yaf.so'
		;;
		'71')
		extFile='/www/server/php/71/lib/php/extensions/no-debug-non-zts-20160303/yaf.so'
		;;
		'71')
		extFile='/www/server/php/71/lib/php/extensions/no-debug-non-zts-20160303/yaf.so'
		;;
		'72')
		extFile='/www/server/php/72/lib/php/extensions/no-debug-non-zts-20170718/yaf.so'
		;;
	esac
	
	isInstall=`cat /www/server/php/$version/etc/php.ini|grep 'yaf.so'`
	if [ "${isInstall}" != "" ];then
		echo "php-$vphp 已安装yaf,请选择其它版本!"
		return
	fi
	
	
	if [ ! -f "$extFile" ];then
		public_file=/www/server/panel/install/public.sh
		if [ ! -f $public_file ];then
			wget -O $public_file http://download.bt.cn/install/public.sh -T 5;
		fi
		. $public_file

		download_Url=$NODE_URL
		
		wafV='2.3.5';
		if [ "$version" = '70' ] || [ "$version" = '71' ] || [ "$version" = '72' ];then
			wafV='3.0.7';
		fi
		wget -O yaf-$wafV.tgz $download_Url/src/yaf-$wafV.tgz
		tar xvf yaf-$wafV.tgz
		cd yaf-$wafV
		
		/www/server/php/$version/bin/phpize
		./configure --with-php-config=/www/server/php/$version/bin/php-config
		make && make install
		cd ..
		rm -rf yaf-*
		rm -f package.xml
	fi
	
	if [ ! -f "$extFile" ];then
		echo "ERROR!"
		return;
	fi
	echo "extension=$extFile" >> /www/server/php/$version/etc/php.ini
	
	service php-fpm-$version reload
	echo '==========================================================='
	echo 'successful!'
}


Uninstall_yaf()
{
	if [ ! -f "/www/server/php/$version/bin/php-config" ];then
		echo "php-$vphp 未安装,请选择其它版本!"
		return
	fi
	
	case "${version}" in 
		'54')
		extFile='/www/server/php/54/lib/php/extensions/no-debug-non-zts-20100525/yaf.so'
		;;
		'55')
		extFile='/www/server/php/55/lib/php/extensions/no-debug-non-zts-20121212/yaf.so'
		;;
		'56')
		extFile='/www/server/php/56/lib/php/extensions/no-debug-non-zts-20131226/yaf.so'
		;;
		'70')
		extFile='/www/server/php/70/lib/php/extensions/no-debug-non-zts-20151012/yaf.so'
		;;
		'71')
		extFile='/www/server/php/71/lib/php/extensions/no-debug-non-zts-20160303/yaf.so'
		;;
		'72')
		extFile='/www/server/php/72/lib/php/extensions/no-debug-non-zts-20170718/yaf.so'
	esac
	if [ ! -f "$extFile" ];then
		echo "php-$vphp 未安装yaf,请选择其它版本!"
		return
	fi
	
	sed -i '/yaf.so/d'  /www/server/php/$version/etc/php.ini
		
	rm -f $extFile
	/etc/init.d/php-fpm-$version reload
	echo '==============================================='
	echo 'successful!'
}


actionType=$1
version=$2
if [ "$actionType" == 'install' ];then
	Install_yaf
elif [ "$actionType" == 'uninstall' ];then
	Uninstall_yaf
fi