#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

action=$1
type=$2

if [ "${2}" == "" ];then
	echo '缺少安装脚本...' > $install_tmp
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...' > $install_tmp
	exit 0
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "uninstall" ];then
	if [ -f /usr/lib/systemd/system/nezha.service ] || [ -f /lib/systemd/system/nezha.service ] ;then
		systemctl stop nezha
		systemctl disable nezha
		rm -rf /usr/lib/systemd/system/nezha.service
		rm -rf /lib/systemd/system/nezha.service
		systemctl daemon-reload
	fi

	if [ -f /usr/lib/systemd/system/nezha-agent.service ] || [ -f /lib/systemd/system/nezha-agent.service ] ;then
		systemctl stop nezha-agent
		systemctl disable nezha-agent
		rm -rf /usr/lib/systemd/system/nezha-agent.service
		rm -rf /lib/systemd/system/nezha-agent.service
		systemctl daemon-reload
	fi
fi
