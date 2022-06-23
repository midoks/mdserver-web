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
cd /www/server/mdserver-web/plugins/openresty && bash install.sh 1.21.4.1
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/openresty/index.py start

# php
cd /www/server/mdserver-web/plugins/php && bash install.sh 71
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/php/index.py start

# mysql
cd /www/server/mdserver-web/plugins/mysql && bash install.sh 5.5
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql/index.py start 5.5


endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"

