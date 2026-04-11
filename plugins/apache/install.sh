#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/apache && bash install.sh install 2.4
# cd /www/server/mdserver-web/plugins/apache && bash install.sh install 2.4
# cd /www/server/mdserver-web/plugins/apache && bash install.sh upgrade 2.4

# curl -I -H "Accept-Encoding: br" http://localhost
# curl -I -H "Accept-Encoding: zstd" http://localhost
# curl --http3 -v https://www.xxx.com

# apt install ncat -y
# nc -u -v www.xx.com 443

# cd /www/server/mdserver-web && python3 plugins/openresty/index.py run_info

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
action=$1
type=$2

VERSION=$2
openrestyDir=${serverPath}/source/apache

if id www &> /dev/null ;then 
    echo "www uid is `id -u www`"
    echo "www shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	useradd -g www -s /bin/bash www
fi

if [ "${action}" == "upgrade" ];then
	sh -x $curPath/versions/$2/install.sh $1
	
	echo "${VERSION}" > $serverPath/apache/version.pl

	mkdir -p $serverPath/web_conf/php/conf
	echo 'set $PHP_ENV 0;' > $serverPath/web_conf/php/conf/enable-php-00.conf

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/apache/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/apache/index.py initd_install
	exit 0
fi


if [ "${2}" == "" ];then
	echo '缺少安装脚本版本...'
	exit 0
fi 

if [ "${action}" == "uninstall" ];then
	if [ -f /usr/lib/systemd/system/apache.service ] || [ -f /lib/systemd/system/apache.service ];then
		systemctl stop apache
		rm -rf /usr/systemd/system/apache.service
		rm -rf /lib/systemd/system/apache.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/apache/init.d/apache ];then
		$serverPath/apache/init.d/apache stop
	fi

	rm -rf $serverPath/apache
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d $serverPath/apache ];then
	echo "${VERSION}" > $serverPath/apache/version.pl

	mkdir -p $serverPath/web_conf/php/conf
	echo 'set $PHP_ENV 0;' > $serverPath/web_conf/php/conf/enable-php-00.conf

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/apache/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/apache/index.py initd_install
fi
