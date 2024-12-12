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


php_fpm_service_file=/lib/systemd/system/php${version}-php-fpm.service
if [ -f /usr/lib/systemd/system/php${version}-php-fpm.service ];then
	php_fpm_service_file=/lib/systemd/system/php${version}-php-fpm.service
fi

php_status=`systemctl status php${version}-php-fpm | grep inactive`
if [ "$php_status" != "" ];then
	systemctl ${action} php${version}-php-fpm
fi

#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

version=$1

if [ "$version" == '5.6' ];then
	echo '20131226'
elif [[ "$version" == '7.0' ]]; then
	echo '20151012'
elif [[ "$version" == '7.1' ]]; then
	echo '20160303'
elif [[ "$version" == '7.2' ]]; then
	echo '20170718'
elif [[ "$version" == '7.3' ]]; then
	echo '20180731'
elif [[ "$version" == '7.4' ]]; then
	echo '20190902'
elif [[ "$version" == '8.0' ]]; then
	echo '20200930'
elif [[ "$version" == '8.1' ]]; then
	echo '20210902'
elif [[ "$version" == '8.2' ]]; then
	echo '20220829'
elif [[ "$version" == '8.3' ]]; then
	echo '20230831'
elif [[ "$version" == '8.4' ]]; then
	echo '20240924'
fi