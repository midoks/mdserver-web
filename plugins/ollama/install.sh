#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

action=$1
type=$2

if [ "${2}" == "" ];then
	echo '缺少安装脚本...'
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...'
	exit 0
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "uninstall" ];then
	if [ -f /usr/lib/systemd/system/ollama.service ] || [ -f /lib/systemd/system/ollama.service ] ;then
		systemctl stop ollama
		systemctl disable ollama
		rm -rf /usr/lib/systemd/system/ollama.service
		rm -rf /lib/systemd/system/ollama.service
		systemctl daemon-reload
	fi
fi
