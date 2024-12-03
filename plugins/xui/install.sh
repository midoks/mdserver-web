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


Install_app()
{
	echo '安装完成'
}

Uninstall_app()
{
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app $2
else
	Uninstall_app $2
fi
