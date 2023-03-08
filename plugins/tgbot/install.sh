#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=$2

# pip3 install ccxt
if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate	
fi

pip3 install pyTelegramBotAPI
pip3 install telebot

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/tgbot
	echo "${VERSION}" > $serverPath/tgbot/version.pl

	cp -rf ${rootPath}/plugins/tgbot/startup/* $serverPath/tgbot

	cd ${rootPath} && python3 ${rootPath}/plugins/tgbot/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/tgbot/index.py initd_install
	echo '安装完成' > $install_tmp
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/tgbot.service ];then
		systemctl stop tgbot
		systemctl disable tgbot
		rm -rf /usr/lib/systemd/system/tgbot.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/tgbot/initd/tgbot ];then
		$serverPath/tgbot/initd/tgbot stop
	fi

	rm -rf $serverPath/tgbot
	echo "Uninstall_redis" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
