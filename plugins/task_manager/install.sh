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

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/task_manager

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
