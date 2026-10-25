#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

version=$1
action=$2

if [ -f /lib/systemd/system/rapira${version}.service ];then
	systemctl ${action} rapira${version}
elif [ -f /usr/lib/systemd/system/rapira${version}.service ]; then
	systemctl ${action} rapira${version}
else
	$serverPath/rapira/init.d/rapira${version} ${action}
fi