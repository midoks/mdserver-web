#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
#+------------------------------------
#+ 释放内存脚本
#+------------------------------------

endDate=`date +"%Y-%m-%d %H:%M:%S"`
sysName=`uname`
curPath=`pwd`
rootPath=$(dirname "$curPath")

log="释放内存!"
echo "★[$endDate] $log"
echo '----------------------------------------------------------------------------'

if [ $sysName == 'Darwin' ]; then
	echo '苹果内存释放!'
else
	echo 'do start!'
fi


echo "OpenResty -- START"
if [ -f /usr/lib/systemd/system/openresty.service ];then
	systemctl reload openresty
elif [ -f $rootPath/openresty/nginx/sbin/nginx ];then
	$rootPath/openresty/nginx/sbin/nginx -s reload
else
	echo "..."
fi	
echo "OpenResty -- END"


PHP_VER_LIST=(53 54 55 56 70 71 72 73 74 80 81)
for PHP_VER in ${PHP_VER_LIST[@]}; do
echo "PHP${PHP_VER} -- START"
if [ -f /usr/lib/systemd/system/php${PHP_VER}.service ];then
	systemctl reload php${PHP_VER}
elif [ -f ${rootPath}/php/init.d/php${PHP_VER} ];then
	${rootPath}/php/init.d/php${PHP_VER} reload
else
	echo "..."
fi
echo "PHP${PHP_VER} -- END"
done

echo "MySQL -- START"
if [ -f /usr/lib/systemd/system/mysql.service ];then
	systemctl reload mysql
elif [ -f ${rootPath}/php/init.d/mysql ];then
	${rootPath}/mysql/init.d/mysql reload
else
	echo "..."
fi
echo "MySQL -- END"



echo "PureFTPD -- START"
if [ -f /usr/lib/systemd/system/pureftp.service ];then
	systemctl reload pureftp
elif [ -f ${rootPath}/pureftp/init.d/pureftp ];then
	${rootPath}/pureftp/init.d/pureftp reload
else
	echo "..."
fi
echo "PureFTPD -- END"


sync
sleep 2
sync

if [ $sysName == 'Darwin' ]; then
	echo 'done!'
else
	echo 3 > /proc/sys/vm/drop_caches
fi

echo '----------------------------------------------------------------------------'