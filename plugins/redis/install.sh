#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web && . ./bin/activate && python3 plugins/redis/index.py upgrade_check 8.8
# cd /www/server/mdserver-web/plugins/redis && bash install.sh install 8.0
# cd /www/server/mdserver-web/plugins/redis && bash install.sh upgrade 8.0

# https://www.cnblogs.com/zlonger/p/16177595.html
# https://www.cnblogs.com/BNTang/articles/15841688.html

# ps -ef|grep redis |grep -v grep | awk '{print $2}' | xargs kill

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/redis && bash install.sh install 7.2.2

# cmd查看| info replication
# /Users/midoks/Desktop/mwdev/server/redis/bin/redis-cli -h 127.0.0.1 -p 6399
# /www/server/redis/bin/redis-cli -h 127.0.0.1 -p 6399

VERSION=$2
action=$1

if [ "${action}" = "upgrade" ];then
	cd ${curPath} && sh -x $curPath/versions/${VERSION}/install.sh upgrade
	which systemctl && systemctl restart redis
	exit 0
fi

if [ "${action}" = "uninstall" ];then
	if [ -f /usr/lib/systemd/system/redis.service ];then
		systemctl stop redis
		systemctl disable redis
		rm -rf /usr/lib/systemd/system/redis.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/redis.service ];then
		systemctl stop redis
		systemctl disable redis
		rm -rf /lib/systemd/system/redis.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/redis/initd/redis ];then
		$serverPath/redis/initd/redis stop
	fi

	if [ -d $serverPath/redis ];then
		rm -rf $serverPath/redis
	fi
fi

cd ${curPath} && sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ];then
	cd ${rootPath} && python3 ${rootPath}/plugins/redis/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/redis/index.py initd_install
fi

