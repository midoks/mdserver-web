#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`
install_tmp=${rootPath}/tmp/mw_install.pl

SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

Install_App()
{
	mkdir -p $serverPath/source/zabbix
	wget -O $serverPath/source/zabbix https://repo.zabbix.com/zabbix/7.0/debian/pool/main/z/zabbix-release/zabbix-release_7.0-2+debian12_all.deb
	cd $serverPath/source/zabbix && dpkg -i zabbix-release_7.0-2+debian12_all.deb
	apt update -y 
}

Uninstall_App()
{
	echo "卸载成功"
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
