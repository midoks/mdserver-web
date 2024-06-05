#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

# python3 plugins/task_manager/task_manager_index.py
# /www/server/mdserver-web/bin/python3 /www/server/mdserver-web/plugins/task_manager/process_network_total.py
# ps -ef|grep process_network_total| grep -v grep | awk '{print $2}' | xargs kill -9

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/task_manager

	if [ -f /usr/bin/apt ]; then
		apt install libpcap-dev -y
	fi

	if [ -f /usr/bin/yum ]; then
		yum install libpcap-devel -y
	fi

	if [ -f /usr/bin/dnf ]; then
		dnf install libpcap-devel -y
	fi

	pip3 install pypcap

	echo "$VERSION" > $serverPath/task_manager/version.pl
	echo "安装任务管理器成功"
}

Uninstall_App()
{	
	rm -rf $serverPath/task_manager
	echo "卸载任务管理器成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
