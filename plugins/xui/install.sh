#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysArch=`arch`
sysName=`uname`


# cd /www/server/mdserver-web && python3 plugins/mtproxy/index.py url
# cd /www/server/mdserver-web/plugins/xui && /bin/bash install.sh install 1.0

VERSION=$2
Install_app()
{
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/xui
	mkdir -p $serverPath/xui

	echo "$VERSION" > $serverPath/xui/version.pl

	bash ${curPath}/install_xui.sh

	x-ui 7

	echo "curPath:$curPath"

	echo '安装完成'
}

Uninstall_app()
{
	rm -rf $serverPath/xui
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app $2
else
	Uninstall_app $2
fi
