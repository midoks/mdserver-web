#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=$2


bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


Install_varnish()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source

	if [ "${OSNAME}" == "macos" ]; then
		brew install varnish
	elif [ "${OSNAME}" == "centos" ] || [ "${OSNAME}" == "fedora" ] || [ "${OSNAME}" == "alma" ] || [ "${OSNAME}" == "rocky" ]; then
		yum install varnish -y
	elif [ "${OSNAME}" == "debian" ] || [ "${OSNAME}" == "ubuntu" ]; then
		apt install varnish -y
	elif [[ "$OSNAME" == "arch" ]]; then
		echo y | pacman -Sy varnish
	elif [ "${OSNAME}" == "opensuse" ];then
		zypper install -y varnish
	else
		echo "I won't support it"
		exit 1
	fi

	mkdir -p $serverPath/varnish
	echo "1.0" > $serverPath/varnish/version.pl
	echo '安装完成'

	cd ${rootPath} && python3 ${rootPath}/plugins/varnish/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/varnish/index.py initd_install
}

Uninstall_varnish()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/varnish/index.py stop
	cd ${rootPath} && python3 ${rootPath}/plugins/varnish/index.py initd_uninstall

	if [ "${OSNAME}" == "macos" ]; then
		brew uninstall varnish
	elif [ "${OSNAME}" == "centos" ] || [ "${OSNAME}" == "fedora" ] || [ "${OSNAME}" == "alma" ] || [ "${OSNAME}" == "rocky" ]; then
		yum remove varnish -y
	elif [ "${OSNAME}" == "debian" ] || [ "${OSNAME}" == "ubuntu" ]; then
		apt remove varnish -y
	elif [[ "$OSNAME" == "arch" ]]; then
		echo y | pacman -Rv varnish
	elif [ "${OSNAME}" == "opensuse" ];then
		zypper remove -y varnish
	else
		echo "I won't support it"
	fi
	rm -rf $serverPath/varnish
	echo "uninstall varnish"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_varnish
else
	Uninstall_varnish
fi
