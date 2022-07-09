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
# PHP_VER_LIST=(81)
for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"
	if [ -d  /www/server/php-apt/${PHP_VER} ];then
		cd /www/server/mdserver-web/plugins/php-apt/versions/${PHP_VER} && bash install.sh install
	fi
	echo "php${PHP_VER} -- end"
done


PHP_EXT_LIST=('yaf')
for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"
	version=${PHP_VER:0}.${PHP_VER:1}
	extVer=`bash $curPath/lib.sh $version`
	
	for EXT in ${PHP_EXT_LIST[@]}; do
		extFile=/usr/lib/php/${extVer}/${LIBNAME}.so
		if [ -f $extFile ];then
			cd $curPath && /bin/bash common.sh  $version  install ${EXT}
		fi
	done

	echo "php${PHP_VER} -- end"
done