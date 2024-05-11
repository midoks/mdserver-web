#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# https://docs.pingcap.com/zh/tidb/stable/quick-start-with-tidb

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/tidb

	app_name=tidb-community-server-${VERSION}-linux-arm64.tar.gz

	if [ ! -f $serverPath/source/tidb/${app_name} ];then
		wget -O $serverPath/source/tidb/${app_name} https://download.pingcap.org/${app_name}
	fi
	
	cd $serverPath/source/tidb && tar -zxvf $serverPath/source/tidb/${app_name}

	if [ -d $serverPath/tidb ];then
		echo "${VERSION}" > $serverPath/tidb/version.pl
		
		cd ${rootPath} && python3 ${rootPath}/plugins/tidb/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/tidb/index.py initd_install
		echo '安装完成'
	else
		echo '安装失败!'
	fi

	if [ -d $serverPath/source/redis-${VERSION} ];then
		rm -rf $serverPath/source/redis-${VERSION}
	fi
}

Uninstall_App()
{
	rm -rf $serverPath/tidb
	echo "卸载TiDB"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
