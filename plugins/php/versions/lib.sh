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

if [ -f /lib/systemd/system/php${version}.service ];then
	systemctl ${action} php${version}
elif [ -f /usr/lib/systemd/system/php${version}.service ]; then
	systemctl ${action} php${version}
else
	$serverPath/php/init.d/php${version} ${action}
fi