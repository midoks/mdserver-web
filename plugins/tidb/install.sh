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

# https://cn.pingcap.com/product-community/
# https://docs.pingcap.com/zh/tidb/stable/quick-start-with-tidb

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/tidb && bash install.sh install v7.5.1
# mw update_dev && cd /www/server/mdserver-web/plugins/tidb && bash install.sh install v7.5.1

# cd /www/server/source/tidb/tidb-community-server-v7.5.1-linux-amd64 && ./local_install.sh

# tiup cluster deploy tidb v7.5.1 /www/server/tidb/tidb.yaml --user root -p -i /root/.ssh/id_rsa
# ssh 192.168.4.1 -l root

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2
TIDB_ARCH=arm64
if [ "$sysArch" == "x86_64" ];then
	TIDB_ARCH=amd64
fi

if [ "$sysArch" == "aarch64" ];then
	TIDB_ARCH=arm64
fi

Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/tidb

	tidb_name=tidb-community-server-${VERSION}-linux-${TIDB_ARCH}
	tidb_toolkit_name=tidb-community-toolkit-${VERSION}-linux-${TIDB_ARCH}
	tgz_name=${tidb_name}.tar.gz
	tgz_toolkit_name=${tidb_toolkit_name}.tar.gz


	if [ ! -f $serverPath/source/tidb/${tgz_name} ];then
		wget -O $serverPath/source/tidb/${tgz_name} https://download.pingcap.org/${tgz_name}
	fi


	if [ ! -d  $serverPath/source/tidb/${tidb_name} ];then
		cd $serverPath/source/tidb && tar -zxvf $serverPath/source/tidb/${tgz_name}
	fi

	if [ ! -f $serverPath/source/tidb/${tgz_toolkit_name} ];then
		wget -O $serverPath/source/tidb/${tgz_name} https://download.pingcap.org/${tgz_toolkit_name}
	fi

	if [ ! -d  $serverPath/source/tidb/${tgz_toolkit_name} ];then
		cd $serverPath/source/tidb && tar -zxvf $serverPath/source/tidb/${tgz_toolkit_name}
	fi

	if [ ! -d $serverPath/tidb/mirror ];then
		mkdir -p $serverPath/tidb/mirror
		cp -rf $serverPath/source/tidb/${tidb_name}/* $serverPath/tidb/mirror
	fi

	cd $serverPath/tidb/mirror && ./local_install.sh

	if [ -d $serverPath/tidb ];then
		echo "${VERSION}" > $serverPath/tidb/version.pl
		
		cd ${rootPath} && python3 ${rootPath}/plugins/tidb/index.py start
		# cd ${rootPath} && python3 ${rootPath}/plugins/tidb/index.py initd_install
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
