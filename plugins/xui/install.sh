#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysArch=`arch`
sysName=`uname`


# cd /www/server/mdserver-web && python3 plugins/xui/index.py info
# cd /www/server/mdserver-web/plugins/xui && /bin/bash install.sh install 1.0

VERSION=$2
Install_app()
{
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/xui
	mkdir -p $serverPath/xui

	echo "$VERSION" > $serverPath/xui/version.pl

	bash ${curPath}/install_xui.sh


	# start xray
	cd /usr/local/x-ui && bin/xray-linux-amd64 -c bin/config.json

	cd ${rootPath} && python3 plugins/xui/index.py start
	echo '安装完成'
}

Uninstall_app()
{
	cd ${rootPath} && python3 plugins/xui/index.py stop
	
	rm -rf $serverPath/xui
	echo 'y' | x-ui uninstall
	rm -rf /usr/bin/x-ui 
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app $2
else
	Uninstall_app $2
fi
