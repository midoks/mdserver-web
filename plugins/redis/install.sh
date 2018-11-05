#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl


Install_redis()
{
	echo '正在安装脚本文件...' > $install_tmp

	echo '安装完成' > $install_tmp
	
}

Uninstall_redis()
{
	echo "Uninstall_redis"
}


action=$1
if [ "${1}" == 'install' ];then
	Install_redis
else
	Uninstall_redis
fi
