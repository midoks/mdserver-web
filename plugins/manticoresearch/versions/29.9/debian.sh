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

mkdir -p $serverPath/manticoresearch
MC_DIR=${serverPath}/source/manticoresearch
mkdir -p $MC_DIR

Install_bullseye()
{
	if [ ! -f $MC_DIR/manticore_${manticore_name}_${arch}.deb ];then
		wget --no-check-certificate -O $MC_DIR/manticore_${manticore_name}_${arch}.deb https://repo.manticoresearch.com/repository/manticoresearch_bullseye/dists/bullseye/main/binary-${sysArch}/manticore_${manticore_name}_${sysArch}.deb
	fi
}

Install_bookworm()
{
	if [ ! -f $MC_DIR/manticore_${manticore_name}_${arch}.deb ];then
		wget --no-check-certificate -O $MC_DIR/manticore_${manticore_name}_${arch}.deb https://repo.manticoresearch.com/repository/manticoresearch_bookworm/dists/bookworm/main/binary-${sysArch}/manticore_${manticore_name}_${sysArch}.deb
	fi
}

Install_none()
{
	echo "none"
	exit 0
}

Install_App()
{
	. /etc/os-release
    echo "Debain 版本: $VERSION_ID"
	
	case "$VERSION_ID" in
		'11') Install_bullseye;;
		'12') ;;
	    '13') Install_bookworm;;
		'*') Install_none;;
	esac

	cd $MC_DIR && apt -y install ./*.deb
	cd $MC_DIR && rm -rf ./*.deb
}

if [ "${action}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_App
else
	echo "OPTIONS ERROR"
fi