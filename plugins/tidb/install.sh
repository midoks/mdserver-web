#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
sysArch=`arch`
echo "use system: ${sysName}"

# https://docs.pingcap.com/zh/tidb/stable/quick-start-with-tidb

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/tidb && bash install.sh install v7.5.1
# cd /www/server/mdserver-web/plugins/tidb && bash install.sh install v7.5.1

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2
TIDB_ARCH=arm64
if [ "$sysArch" == "x86_64" ];then
	TIDB_ARCH=amd
fi

if [ "$sysArch" == "aarch64" ];then
	TIDB_ARCH=arm64
fi

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/tidb

	app_name=tidb-community-server-${VERSION}-linux-${TIDB_ARCH}.tar.gz

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
