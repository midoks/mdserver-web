#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/dynamic-tracking && /bin/bash install.sh uninstall 1.0
# cd /www/server/mdserver-web/plugins/dynamic-tracking && /bin/bash install.sh install 1.0

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

Install_App()
{

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/dynamic-tracking


	echo "开发中..."


	echo "${VERSION}" > $serverPath/dynamic-tracking/version.pl
	echo '安装完成' > $install_tmp

	cd ${rootPath} && python3 ${rootPath}/plugins/dynamic-tracking/index.py start
	# cd ${rootPath} && python3 ${rootPath}/plugins/dynamic-tracking/index.py initd_install

}

Uninstall_Docker()
{
	rm -rf $serverPath/dynamic-tracking
	echo "Uninstall_App" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
