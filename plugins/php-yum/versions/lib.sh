#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

version=$1
action=$2


php_status=`systemctl status php${version}-php-fpm | grep inactive`
if [ "$php_status" != "" ];then
	systemctl ${action} php${version}-php-fpm
fi

if [ -f /lib/systemd/system/php${version}-php-fpm.service ];then
	systemctl ${action} php${version}-php-fpm
elif [ -f /usr/lib/systemd/system/php${version}-php-fpm.service ]; then
	systemctl ${action} php${version}-php-fpm
else
	$serverPath/php/init.d/php${version} ${action}
fi