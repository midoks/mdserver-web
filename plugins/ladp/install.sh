#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# https://www.cnblogs.com/zlonger/p/16177595.html
# https://www.cnblogs.com/BNTang/articles/15841688.html

# ps -ef|grep redis |grep -v grep | awk '{print $2}' | xargs kill

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/redis && bash install.sh install 7.2.2

# cmd查看| info replication
# /Users/midoks/Desktop/mwdev/server/redis/bin/redis-cli -h 127.0.0.1 -p 6399
# /www/server/redis/bin/redis-cli -h 127.0.0.1 -p 6399

VERSION=$2

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source
}

Uninstall_App()
{	
	echo "卸载redis成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
