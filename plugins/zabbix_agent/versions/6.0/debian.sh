#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`

SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

Install_App()
{
	mkdir -p $serverPath/source/zabbix

	ZABBIX_NAME=zabbix-release_6.0-5+debian${SYS_VERSION_ID}_all.deb
	echo "wget -O $serverPath/source/zabbix/${ZABBIX_NAME} https://repo.zabbix.com/zabbix/6.0/debian/pool/main/z/zabbix-release/${ZABBIX_NAME}"
	if [ ! -f  $serverPath/source/zabbix/${ZABBIX_NAME} ];then
		wget -O $serverPath/source/zabbix/${ZABBIX_NAME} https://repo.zabbix.com/zabbix/6.0/debian/pool/main/z/zabbix-release/${ZABBIX_NAME}
	fi

	cd $serverPath/source/zabbix && dpkg -i ${ZABBIX_NAME}
	apt update -y 

	apt install -y zabbix-agent
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
