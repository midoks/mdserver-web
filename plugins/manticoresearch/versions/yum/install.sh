#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`


if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

VERSION=$2

Install_App()
{
	echo '正在安装manticoresearch...'
	mkdir -p $serverPath/manticoresearch

	MC_DIR=${serverPath}/source/manticoresearch
	mkdir -p $MC_DIR

	wget --no-check-certificate -O $MC_DIR/manticore-repo.noarch.deb https://repo.manticoresearch.com/manticore-repo.noarch.deb
	dpkg -i $MC_DIR/manticore-repo.noarch.deb
	apt update -y 
	apt -y install manticore manticore-extra


	echo "${VERSION}" > $serverPath/manticoresearch/version.pl

	if [ -d ${MC_DIR} ];then
		rm -rf ${MC_DIR}
	fi
}

Uninstall_App()
{
	yum -y uninstall manticore manticore-extra

	if [ -d $serverPath/manticoresearch ];then
		rm -rf $serverPath/manticoresearch
	fi

	echo "卸载manticoresearch成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
