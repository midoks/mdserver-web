#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# https://www.zabbix.com

# cd /www/server/mdserver-web/plugins/zabbix_agent && /bin/bash install.sh install 7.0
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/zabbix_agent/index.py start


# /usr/sbin/zabbix_agentd -c /etc/zabbix/zabbix_agentd.conf

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=$2

sysName=`uname`
echo "use system: ${sysName}"

OSNAME=`bash ${rootPath}/scripts/getos.sh`

if [ "" == "$OSNAME" ];then
	OSNAME=`cat ${rootPath}/data/osname.pl`
fi

if [ "macos" == "$OSNAME" ];then
	echo "不支持Macox"
	exit
fi

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source/zabbix_agent
	shell_file=${curPath}/versions/${VERSION}/${OSNAME}.sh

	if [ -f $shell_file ];then
		bash -x $shell_file install
	else
		echo '不支持...'
		exit 1
	fi


	mkdir -p $serverPath/zabbix_agent
	echo "${VERSION}" > $serverPath/zabbix_agent/version.pl

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/zabbix_agent/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/zabbix_agent/index.py initd_install


	echo 'Zabbix安装完成'
}

Uninstall_App()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/zabbix_agent/index.py stop
	cd ${rootPath} && python3 ${rootPath}/plugins/zabbix_agent/index.py initd_uninstall

	rm -rf $serverPath/zabbix_agent
	rm -rf $serverPath/source/zabbix_agent
	echo 'Zabbix卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
