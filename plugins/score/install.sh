#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl

Install_score()
{
	echo '正在安装脚本文件...' > $install_tmp

	mkdir -p $serverPath/score
	
	gcc $curPath/testcpu.c -o $serverPath/score/testcpu -lpthread
	if [ ! -f $serverPath/score/testcpu ];then
		sleep 0.1
		gcc $curPath/testcpu.c -o $serverPath/score/testcpu -lpthread
	fi
	
	echo '安装完成' > $install_tmp
}

Uninstall_score()
{
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_score
else
	Uninstall_score
fi
