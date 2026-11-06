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
	echo "${VERSION}" > $serverPath/manticoresearch/version.pl

	if grep -qi '^ID=ubuntu' /etc/os-release; then
	    . /etc/os-release
	    echo "Ubuntu 版本: $VERSION_ID"
	    echo "完整版本: $PRETTY_NAME"
	fi


	echo "install manticoresearch successful!"
}

Uninstall_App()
{
	cd ${rootPath} && python3 plugins/manticoresearch/index.py stop ${VERSION}
	cd ${rootPath} && python3 plugins/manticoresearch/index.py initd_uninstall ${VERSION}

	if [ -d $serverPath/manticoresearch ];then
		rm -rf $serverPath/manticoresearch
	fi
	
	if [ -f /usr/lib/systemd/system/manticore.service ] || [ -f /lib/systemd/system/manticore.service ];then
		systemctl stop manticore
		systemctl disable manticore
		rm -rf /usr/lib/systemd/system/manticore.service
		rm -rf /lib/systemd/system/manticore.service
		systemctl daemon-reload
	fi

	echo "uninstall manticoresearch successful!"
}

if [ "${1}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_App
elif [ "${1}" = 'uninstall' ];then
	Uninstall_App
else
	echo "OPTIONS ERROR"
fi