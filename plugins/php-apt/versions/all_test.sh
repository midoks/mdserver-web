#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/php-apt/versions && /bin/bash all_test.sh


# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php-apt/index.py start 5.6


# cd /www/server/mdserver-web
# cd /www/server/mdserver-web/plugins/php-apt/versions && /bin/bash common.sh  5.6  install yaf
# cd /www/server/mdserver-web/plugins/php-apt/versions && /bin/bash common.sh  7.1  install swoole


PHP_VER_LIST=(56 70 71 72 73 74 80 81 82 83 84)
for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"
	if [ ! -d  /www/server/php-apt/${PHP_VER} ];then
		cd /www/server/mdserver-web/plugins/php-apt && bash install.sh install ${PHP_VER}
	fi
	echo "php${PHP_VER} -- end"
done


cd $curPath

PHP_VER_LIST_EXT=(56 70 71 72 73 74 80 81 82 83 84)
PHP_EXT_LIST=(ioncube pdo mysqlnd sqlite3 odbc opcache mcrypt fileinfo \
	exif gd intl memcache memcached redis imagick xdebug xhprof \
	swoole yaf phalcon yar mongodb yac solr seaslog mbstring zip zstd)
for PHP_VER in ${PHP_VER_LIST_EXT[@]}; do
	echo "php${PHP_VER} EXT -- start"
	version=${PHP_VER:0:1}.${PHP_VER:1:2}
	extVer=`bash $curPath/lib.sh $version`
	
	for EXT in ${PHP_EXT_LIST[@]}; do
		extFile=/usr/lib/php/${extVer}/${EXT}.so
		echo "${PHP_VER} ${EXT} start"
		if [ ! -f $extFile ];then
			/bin/bash common.sh  $version  install ${EXT}
		fi
		echo "${PHP_VER} ${EXT} end"
	done

	echo "php${PHP_VER} EXT -- end"
done


