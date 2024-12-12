#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
SYSOS=`uname`

VERSION=$2

# cd /www/server/mdserver-web/plugins/swap && /bin/bash install.sh install 1.1

Install_swap()
{
	if [ -d $serverPath/swap ];then
		exit 0
	fi

	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source
	mkdir -p $serverPath/swap
	echo "${VERSION}" > $serverPath/swap/version.pl

	if [ "$sysName" == "Darwin" ];then
		pass
	else
		dd if=/dev/zero of=$serverPath/swap/swapfile bs=1M count=1024
		chmod 600 $serverPath/swap/swapfile
		mkswap $serverPath/swap/swapfile
		swapon $serverPath/swap/swapfile
	fi 

	echo '安装完成'

	cd ${rootPath} && python3 ${rootPath}/plugins/swap/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/swap/index.py initd_install
}

Uninstall_swap()
{
	swapoff $serverPath/swap/swapfile


	if [ -f /usr/lib/systemd/system/swap.service ] || [ -f /lib/systemd/system/swap.service ];then
		systemctl stop swap
		systemctl disable swap
		rm -rf /usr/lib/systemd/system/swap.service
		rm -rf /lib/systemd/system/swap.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/swap/initd/swap ];then
		$serverPath/swap/initd/swap stop
	fi

	rm -rf $serverPath/swap
	
	echo "Uninstall_swap"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_swap
else
	Uninstall_swap
fi
