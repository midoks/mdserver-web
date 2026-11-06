#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# https://manticoresearch.com/zh/install/

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`dpkg --print-architecture`

if [ -f ${rootPath}/bin/activate ];then
	. ${rootPath}/bin/activate
fi

VERSION=$2
action=$1

manticore_name=29.9.0-26091108-58e88d5ab
Install_App()
{
	. /etc/os-release
    echo "Ubuntu 版本: $VERSION_ID"
    echo "完整版本: $PRETTY_NAME"
	mkdir -p $serverPath/manticoresearch

	MC_DIR=${serverPath}/source/manticoresearch
	mkdir -p $MC_DIR

	if [ ! -f $MC_DIR/manticore-repo.noarch.deb ];then
		wget --no-check-certificate -O $MC_DIR/manticore-repo.noarch.deb https://repo.manticoresearch.com/repository/manticoresearch_jammy/dists/jammy/main/binary-${arch}/manticore_${manticore_name}_${arch}.deb
	fi
	apt -y update 
	cd $MC_DIR && apt -y install ./*.deb
}

if [ "${action}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_App
else
	echo "OPTIONS ERROR"
fi