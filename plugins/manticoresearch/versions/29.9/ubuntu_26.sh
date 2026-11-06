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
	. ${rootPath}/bin/activate
fi

VERSION=$2
action=$1
manticore_name=29.0.2-26081409-2f9c226b6-osx11.6-arm64

Install_App()
{
	echo '正在安装manticoresearch...'
	mkdir -p $serverPath/manticoresearch

	MC_DIR=${serverPath}/source/manticoresearch
	mkdir -p $MC_DIR

	# https://github.com/manticoresoftware/manticoresearch/archive/refs/tags/release-29.9.0.tar.gz
	# https://repo.manticoresearch.com/repository/manticoresearch_macos/release/manticore-29.0.2-26081409-2f9c226b6-osx11.6-arm64.tar.gz
	if [ ! -f $MC_DIR/manticore-${manticore_name}.tar.gz ];then
		wget --no-check-certificate -O $MC_DIR/manticore-${manticore_name}.tar.gz https://repo.manticoresearch.com/repository/manticoresearch_macos/release/manticore-${manticore_name}.tar.gz
	fi

	mkdir -p $MC_DIR/manticore
	if [ ! -d $MC_DIR/manticore-${manticore_name} ];then
		 cd $MC_DIR/manticore && tar -zxvf $MC_DIR/manticore-${manticore_name}.tar.gz
	fi

	cd $MC_DIR/manticore && cp -rf ./* $serverPath/manticoresearch/

	echo "${VERSION}" > $serverPath/manticoresearch/version.pl
	cd ${rootPath} && python3 plugins/manticoresearch/index.py start ${VERSION}
	cd ${rootPath} && python3 plugins/manticoresearch/index.py initd_install ${VERSION}

	# if [ -d $MC_DIR/manticore-${manticore_name} ];then
	# 	rm -rf $MC_DIR/manticore-${manticore_name}
	# fi
	echo "install manticoresearch successful!"
}

if [ "${1}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_App
else
	echo "OPTIONS ERROR"
fi