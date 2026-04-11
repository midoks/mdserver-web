#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/caddy && bash install.sh install 1.21.4
# cd /www/server/mdserver-web/plugins/caddy && bash install.sh install 1.21.4
# cd /www/server/mdserver-web/plugins/caddy && bash install.sh install 1.29.2
# cd /www/server/mdserver-web/plugins/caddy && bash install.sh upgrade 1.29.2

# curl -I -H "Accept-Encoding: br" http://localhost
# curl -I -H "Accept-Encoding: zstd" http://localhost
# curl --http3 -v https://www.xxx.com

# cd /www/server/mdserver-web && python3 plugins/caddy/index.py run_info

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
action=$1
type=$2

VERSION=$2
openrestyDir=${serverPath}/source/caddy

if id www &> /dev/null ;then 
    echo "www uid is `id -u www`"
    echo "www shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	useradd -g www -s /bin/bash www
fi

if [ "${action}" == "upgrade" ];then
	sh -x $curPath/versions/$2/install.sh $1
	
	echo "${VERSION}" > $serverPath/caddy/version.pl

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/caddy/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/caddy/index.py initd_install
	exit 0
fi


if [ "${2}" == "" ];then
	echo '缺少安装脚本版本...'
	exit 0
fi 

if [ "${action}" == "uninstall" ];then
	if [ -f /usr/lib/systemd/system/caddy.service ] || [ -f /lib/systemd/system/caddy.service ];then
		systemctl stop caddy
		rm -rf /usr/systemd/system/caddy.service
		rm -rf /lib/systemd/system/caddy.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/caddy/init.d/caddy ];then
		$serverPath/caddy/init.d/caddy stop
	fi

	rm -rf $serverPath/caddy
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d $serverPath/caddy ];then
	echo "${VERSION}" > $serverPath/caddy/version.pl

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/caddy/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/caddy/index.py initd_install
fi
