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
else
	echo "openresty alreay exist!"
fi


# php
if [ ! -d /www/server/php/71 ];then
	cd /www/server/mdserver-web/plugins/php && bash install.sh install 71
else
	echo "php71 alreay exist!"
fi


# php
if [ ! -d /www/server/php/74 ];then
	cd /www/server/mdserver-web/plugins/php && bash install.sh install 74
else
	echo "php74 alreay exist!"
fi


# swap
if [ ! -d /www/server/swap ];then
	cd /www/server/mdserver-web/plugins/swap && bash install.sh install 1.1
else
	echo "swap alreay exist!"
fi

# mysql
if [ ! -d /www/server/mysql ];then
	cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 5.6
else
	echo "mysql alreay exist!"
fi

# phpmyadmin
if [ ! -d /www/server/phpmyadmin ];then
	cd /www/server/mdserver-web/plugins/phpmyadmin && bash install.sh install 4.4.15
else
	echo "phpmyadmin alreay exist!"
fi

endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"

} 1> >(tee /www/server/mdserver-web/logs/mw-app.log) 2>&1