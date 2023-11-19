#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

if [ ! -d /www/server/mdserver-web/logs ]; then
	mkdir -p /www/server/mdserver-web/logs
fi

{

echo "welcome to mdserver-web panel"

startTime=`date +%s`

if [ ! -d /www/server/mdserver-web ];then
	echo "mdserver-web not exist!"
	exit 1
fi

# openresty
if [ ! -d /www/server/openresty ];then
	cd /www/server/mdserver-web/plugins/openresty && bash install.sh install 1.21.4.1
fi


# php
# if [ ! -d /www/server/php/71 ];then
# 	cd /www/server/mdserver-web/plugins/php && bash install.sh install 71
# fi


PHP_VER_LIST=(53 54 55 56 70 71 72 73 74 80 81 82)
# PHP_VER_LIST=(81)
for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"
	if [ ! -d  /www/server/php/${PHP_VER} ];then
		cd /www/server/mdserver-web/plugins/php && bash install.sh install ${PHP_VER}
	fi
	echo "php${PHP_VER} -- end"
done


# cd /www/server/mdserver-web/plugins/php-yum && bash install.sh install 74


# mysql
if [ ! -d /www/server/mysql ];then
	# cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 5.7


	cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 5.6
	# cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 8.0
fi

endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"

} 1> >(tee /www/server/mdserver-web/logs/mw-debug.log) 2>&1