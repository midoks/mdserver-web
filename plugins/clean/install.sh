#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4
# cd /www/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi


Install_app()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/clean

	cd ${rootPath} && python3 ${rootPath}/plugins/clean/index.py start
	echo "${VERSION}" > $serverPath/clean/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_app()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/clean/index.py stop
	rm -rf $serverPath/clean
	echo "Uninstall_clean" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app
else
	Uninstall_app
fi
