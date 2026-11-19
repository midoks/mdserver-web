#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/clean && /bin/bash install.sh install
# cd /www/server/mdserver-web && . bin/activate && python3 plugins/clean/index.py clean

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=$2
action=$1

if [ -f ${rootPath}/bin/activate ];then
	. ${rootPath}/bin/activate
fi


Install_app()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/clean

	cd ${rootPath} && python3 ${rootPath}/plugins/clean/index.py start
	echo "${VERSION}" > $serverPath/clean/version.pl
	echo '安装完成'
}

Uninstall_app()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/clean/index.py stop
	rm -rf $serverPath/clean
	echo "Uninstall_clean"
}


if [ "${action}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_app
elif [ "${action}" = 'uninstall' ];then
	Uninstall_app
else
	echo "OPTIONS ERROR"
fi
