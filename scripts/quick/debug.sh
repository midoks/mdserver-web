#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

echo "welcome to mdserver-web panel"

startTime=`date +%s`

if [ ! -d /www/server/mdserver-web ];then
	echo "mdserver-web not exist!"
	exit 1
fi

# openresty
if [ ! -d /www/server/openresty ];then
	cd /www/server/mdserver-web/plugins/openresty && bash install.sh install 1.21.4.1
	cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/openresty/index.py start
fi


# php
if [ ! -d /www/server/php/71 ];then
	cd /www/server/mdserver-web/plugins/php && bash install.sh install 71
	cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 71
fi



# PHP_VER_LIST=(53 54 55 56 71 72 73 74 80 81)
# # PHP_VER_LIST=(81)
# for PHP_VER in ${PHP_VER_LIST[@]}; do
# 	echo "php${PHP_VER} -- start"
# 	cd $DIR/php$PHP_VER && sh install.sh
# 	dir=$(ls -l $DIR/php$PHP_VER |awk '/^d/ {print $NF}')
# 	for i in $dir
# 	do
# 		cd $DIR/php$PHP_VER/$i && sh install.sh $PHP_VER
# 	done
# 	echo "php${PHP_VER} -- end"
# done

cd /www/server/mdserver-web/plugins/php && bash install.sh install 53
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 53

cd /www/server/mdserver-web/plugins/php && bash install.sh install 54
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 54

cd /www/server/mdserver-web/plugins/php && bash install.sh install 55
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 55

cd /www/server/mdserver-web/plugins/php && bash install.sh install 56
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 56
cd /www/server/mdserver-web/plugins/php && bash install.sh install 70
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 70
cd /www/server/mdserver-web/plugins/php && bash install.sh install 71
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 71

cd /www/server/mdserver-web/plugins/php && bash install.sh install 72
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 72

cd /www/server/mdserver-web/plugins/php && bash install.sh install 73
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 73

cd /www/server/mdserver-web/plugins/php && bash install.sh install 74
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 74

cd /www/server/mdserver-web/plugins/php && bash install.sh install 80
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 80

cd /www/server/mdserver-web/plugins/php && bash install.sh install 81
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start 81


# mysql
if [ ! -d /www/server/mysql ];then
	# cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 5.7
	# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql/index.py start 5.7


	# cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 5.6
	# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql/index.py start 5.6
	cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 8.0
	cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql/index.py start 8.0
fi

endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"

