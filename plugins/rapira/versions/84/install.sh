#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`
OS_ARCH=`arch`

sys_name=linux
if [ "$sysName" == "Darwin" ];then
	sys_name=macos
fi

sys_arch="x86_64"
if [ "$OS_ARCH" == "arm64" ];then
	sys_arch=aarch64
fi

rapira_version=0.9.1
version_min=8.4
version=8.4.26
PHP_VER=84
md5_file_ok=32a2de53862ad44ed4a5005244ce4f1b50c271e74dced215449a4443b40569f1
Install_php()
{
#------------------------ install start ------------------------------------#
echo "安装rapira-${version} ..."
mkdir -p $sourcePath/rapira
mkdir -p $serverPath/rapira



if [ ! -d $sourcePath/rapira/rapira-${rapira_version} ];then
	if [ ! -f $sourcePath/rapira/rapira-${rapira_version}.tar.gz ];then
		
		wget --no-check-certificate -O $sourcePath/rapira/rapira-${rapira_version}.tar.gz https://github.com/rapira-rs/rapira/releases/download/v${rapira_version}/rapira-v${rapira_version}-php${version_min}-${sys_name}-${sys_arch}.tar.gz
	fi
	
	cd $sourcePath/rapira && tar -zxvf $sourcePath/rapira/rapira-${rapira_version}.tar.gz
fi

#------------------------ install end ------------------------------------#
}

Uninstall_php()
{
	# $serverPath/php/init.d/php${PHP_VER} stop
	# rm -rf $serverPath/php/${PHP_VER}
	echo "卸载php-${version}..."
}

action=${1}
if [ "${1}" = 'install' ];then
	Install_php
else
	Uninstall_php
fi
