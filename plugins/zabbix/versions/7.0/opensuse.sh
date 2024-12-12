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

# 检查是否通
# zabbix_get -s 127.0.0.1 -k agent.ping
Install_App()
{
	yum install -y glibc-langpack-zh

	mkdir -p $serverPath/source/zabbix



	ZABBIX_NAME=zabbix-release-7.0-2.sles${SYS_VERSION_ID:0:2}.noarch.rpm

	rpm -Uvh https://repo.zabbix.com/zabbix/7.0/sles/${SYS_VERSION_ID:0:2}/x86_64/${ZABBIX_NAME}
	echo "rpm -Uvh https://repo.zabbix.com/zabbix/7.0/sles/${SYS_VERSION_ID:0:2}/x86_64/${ZABBIX_NAME}"


	# debug
	# symbol lookup error: /usr/sbin/zabbix_server: undefined symbol: usmAES256CiscoPrivProtocol
	# /usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf

	# zypper update -y net-snmp
	# zypper update -y net-snmp-utils
	# zypper install -y net-snmp-devel
	
	zypper install -y zabbix-server-mysql
	zypper install -y zabbix-web-mysql 
	zypper install -y zabbix-sql-scripts
	zypper install -y zabbix-agent
}

Uninstall_App()
{
	zypper remove -y zabbix-server-mysql
	zypper remove -y zabbix-web-mysql
	zypper remove -y zabbix-sql-scripts
	zypper remove -y zabbix-agent
	rm -rf /etc/zabbix
	echo "卸载成功"
}

action=${1}
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
