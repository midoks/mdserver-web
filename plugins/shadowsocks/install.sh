#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl

SYSOS=`uname`

Install_shadowsocks()
{
	isStart=""
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/shadowsocks
	echo '1.0' > $serverPath/shadowsocks/version.pl

	pip install shadowsocks
	cat $curPath/tmp/shadowsocks.json > $serverPath/shadowsocks/shadowsocks.json

	echo 'install complete' > $install_tmp
}

Uninstall_shadowsocks()
{
	rm -rf $serverPath/shadowsocks
	echo "Uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_shadowsocks
else
	Uninstall_shadowsocks
fi
