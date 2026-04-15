#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/caddy && bash install.sh install 2.11
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/caddy && bash install.sh upgrade 2.11
# cd /www/server/mdserver-web/plugins/caddy && bash install.sh install 2.11

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
action=$1
type=$2

OS=`uname`
OSNAME=''
case $(uname) in
    Darwin)   OSNAME="mac" ;;
    Linux)   OSNAME="linux" ;;
esac

ARCH=`uname -m`
ARCH_NAME=''
case $(uname -m) in
    i386)   ARCH_NAME="386" ;;
    i686)   ARCH_NAME="386" ;;
    x86_64) ARCH_NAME="amd64" ;;
    arm)    ARCH_NAME="arm64" ;;
	arm64)  ARCH_NAME="arm64" ;;
esac

VERSION=2.11.2

caddyDir=${serverPath}/source/caddy

Install_App()
{
	if [ "${action}" == "install" ];then
		if [ -d $serverPath/caddy ];then
			exit 0
		fi
	fi

	mkdir -p ${caddyDir}
	# mkdir -p ${serverPath}/caddy
	echo 'install scripts ...'

	FILE_NAME="caddy_${VERSION}_${OSNAME}_${ARCH_NAME}.tar.gz"

	if [ ! -f ${caddyDir}/${FILE_NAME} ];then
		wget --no-check-certificate -O ${caddyDir}/${FILE_NAME} "https://github.com/caddyserver/caddy/releases/download/v${VERSION}/${FILE_NAME}"
	fi


	echo "cd $serverPath/source/caddy/caddy && tar -zxvf ${caddyDir}/$FILE_NAME"

	mkdir -p cd $serverPath/source/caddy/caddy
	cd $serverPath/source/caddy/caddy && tar -zxvf ${caddyDir}/$FILE_NAME
	if [ "$OSNAME" == "mac" ];then
		xattr -cr caddy
	fi

	if [ ! -f $serverPath/caddy/bin ];then
		mkdir -p $serverPath/caddy/bin
		mv $serverPath/source/caddy/caddy/* $serverPath/caddy/bin
		chmod +x $serverPath/caddy/bin/caddy
	fi

	echo 'Installation of caddy completed'
}

Uninstall_App()
{
	echo 'Uninstalling caddy completed'
}

action=$1
if [ "${1}" == "install" ];then
	Install_App
elif [ "${1}" == "upgrade" ];then
	Install_App
else
	Uninstall_App
fi
