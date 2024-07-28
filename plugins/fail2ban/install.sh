#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

# cd /www/server/mdserver-web/plugins/fail2ban && bash install.sh install 1.1.0

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	apt install -y fail2ban

	mkdir -p $serverPath/fail2ban
	sed '/^ *#/d' fail2ban.conf > $serverPath/fail2ban/redis.conf

	echo "${VERSION}" > $serverPath/fail2ban/version.pl
	echo '安装fail2ban完成'

	cd ${rootPath} && python3 ${rootPath}/plugins/fail2ban/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/fail2ban/index.py initd_install
		

}

Uninstall_App()
{
	apt remove -y fail2ban


	if [ -f /usr/lib/systemd/system/fail2ban.service ];then
		systemctl stop fail2ban
		systemctl disable fail2ban
		rm -rf /usr/lib/systemd/system/fail2ban.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/fail2ban.service ];then
		systemctl stop fail2ban
		systemctl disable fail2ban
		rm -rf /lib/systemd/system/fail2ban.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/fail2ban/initd/fail2ban ];then
		$serverPath/fail2ban/initd/fail2ban stop
	fi

	if [ -d $serverPath/fail2ban ];then
		rm -rf $serverPath/fail2ban
	fi
	
	echo "卸载fail2ban成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
