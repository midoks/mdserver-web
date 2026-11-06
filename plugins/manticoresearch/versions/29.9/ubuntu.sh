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

Install_bionic()
{
	if [ ! -f $MC_DIR/manticore-repo.noarch.deb ];then
		wget --no-check-certificate -O $MC_DIR/manticore-repo.noarch.deb https://repo.manticoresearch.com/repository/manticoresearch_bionic/dists/bionic/main/binary-${arch}/manticore_${manticore_name}_${arch}.deb
	fi
}

Install_focal()
{
	if [ ! -f $MC_DIR/manticore-repo.noarch.deb ];then
		wget --no-check-certificate -O $MC_DIR/manticore-repo.noarch.deb https://repo.manticoresearch.com/repository/manticoresearch_focal/dists/focal/main/binary-${arch}/manticore_${manticore_name}_${arch}.deb
	fi
}

Install_jammy()
{
	if [ ! -f $MC_DIR/manticore-repo.noarch.deb ];then
		wget --no-check-certificate -O $MC_DIR/manticore-repo.noarch.deb https://repo.manticoresearch.com/repository/manticoresearch_jammy/dists/jammy/main/binary-${arch}/manticore_${manticore_name}_${arch}.deb
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
    echo "Ubuntu 版本: $VERSION_ID"
    # echo "完整版本: $PRETTY_NAME"

	case "$VERSION_ID" in
		'18.04') Install_bionic;;
		'20.04') Install_focal;;
		'22.04') ;;
	    '24.04') ;;
	    '26.04') Install_jammy;;
		'*') Install_none;;
	esac

	apt -y update 
	cd $MC_DIR && apt -y install ./*.deb
	cd $MC_DIR && rm -rf ./*.deb
}

if [ "${action}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_App
else
	echo "OPTIONS ERROR"
fi