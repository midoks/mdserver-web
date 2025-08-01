#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# https://www.cnblogs.com/n00dle/p/16916044.html
# cd /www/server/mdserver-web/plugins/grafana && /bin/bash install.sh install 12.1.0
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/grafana/index.py start

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=$2

sysArch=`arch`
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

if id grafana &> /dev/null ;then 
    echo "grafana uid is `id -u grafana`"
    echo "grafana shell is `grep "^grafana:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd grafana
	useradd -g grafana -s /bin/bash grafana
fi

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source/grafana

	mkdir -p $serverPath/grafana
	echo "${VERSION}" > $serverPath/grafana/version.pl

	shell_file=${curPath}/versions/${VERSION}/linux.sh

	if [ -f $shell_file ];then
		bash -x $shell_file install ${VERSION}
	else
		echo '不支持...'
		exit 1
	fi

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/grafana/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/grafana/index.py initd_install

	echo 'Grafana安装完成'
}

Uninstall_App()
{
	shell_file=${curPath}/versions/${VERSION}/linux.sh
	if [ -f $shell_file ];then
		bash -x $shell_file uninstall ${VERSION}
	fi

	cd ${rootPath} && python3 ${rootPath}/plugins/grafana/index.py stop
	cd ${rootPath} && python3 ${rootPath}/plugins/grafana/index.py initd_uninstall

	rm -rf $serverPath/grafana
	echo 'Grafana卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
