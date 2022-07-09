#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/php-apt/versions && /bin/bash all_test.sh


# cd /www/server/mdserver-web
# cd /www/server/mdserver-web/plugins/php-apt/versions && /bin/bash common.sh  5.6  install yaf


PHP_VER_LIST=(56 70 71 72 73 74 80 81)
for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"
	if [ ! -d  /www/server/php-apt/${PHP_VER} ];then
		cd /www/server/mdserver-web/plugins/php-apt && bash install.sh install ${PHP_VER}
	fi
	echo "php${PHP_VER} -- end"
done

PHP_VER_LIST_EXT=(56 70 71 72 73 74 80 81)
PHP_EXT_LIST=(yaf pdo mysqlnd sqlite3)
for PHP_VER in ${PHP_VER_LIST_EXT[@]}; do
	echo "php${PHP_VER} EXT -- start"
	version=${PHP_VER:0:1}.${PHP_VER:1:2}
	extVer=`bash $curPath/lib.sh $version`
	
	for EXT in ${PHP_EXT_LIST[@]}; do
		extFile=/usr/lib/php/${extVer}/${EXT}.so
		echo "${EXT} start"
		if [ ! -f $extFile ];then
			cd $curPath && /bin/bash common.sh  $version  install ${EXT}
		fi
		echo "${EXT} end"
	done

	echo "php${PHP_VER} EXT -- end"
done