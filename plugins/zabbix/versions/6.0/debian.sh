#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`

debian_suffix=
if [ "$SYS_ARCH" == "aarch64" ];then
	debian_suffix="-arm64"
fi

SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

# 检查是否通
# zabbix_get -s 127.0.0.1 -k agent.ping
Install_App()
{
	mkdir -p $serverPath/source/zabbix

	ZABBIX_NAME=zabbix-release_6.0-5+debian${SYS_VERSION_ID}_all.deb
	echo "wget -O $serverPath/source/zabbix/${ZABBIX_NAME} https://repo.zabbix.com/zabbix/6.0/debian${debian_suffix}/pool/main/z/zabbix-release/${ZABBIX_NAME}"
	if [ ! -f  $serverPath/source/zabbix/${ZABBIX_NAME} ];then
		wget -O $serverPath/source/zabbix/${ZABBIX_NAME} https://repo.zabbix.com/zabbix/6.0/debian${debian_suffix}/pool/main/z/zabbix-release/${ZABBIX_NAME}
	fi

	dpkg --configure -a
	cd $serverPath/source/zabbix && dpkg -i ${ZABBIX_NAME}
	apt update -y 
	rm -rf /etc/zabbix/zabbix_server.conf.dpkg-new
	rm -rf /etc/zabbix/zabbix_server.conf
	apt install -y zabbix-server-mysql zabbix-frontend-php zabbix-sql-scripts zabbix-agent zabbix-get
}

Uninstall_App()
{
	apt remove -y zabbix-server-mysql zabbix-frontend-php zabbix-sql-scripts zabbix-agent zabbix-get
	rm -rf /etc/zabbix
	dpkg --configure -a
	echo "卸载成功"
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
