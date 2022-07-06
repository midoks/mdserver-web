#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=$2

_os=`uname`
if [ ${_os} == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eq "openSUSE" /etc/*-release; then
	OSNAME='opensuse'
elif grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
elif grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
elif grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
elif grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
else
	OSNAME='unknow'
fi

Install_varnish()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	if [ ${OSNAME} == "macos" ]; then
		brew install varnish
	elif [ ${OSNAME} == "centos" ]; then
		yum install varnish -y
	elif [ ${OSNAME} == "debian" ] || [ ${OSNAME} == "ubuntu" ]; then
		apt install varnish -y
	elif [ ${OSNAME} == "opensuse" ];then
		zypper install -y varnish
	else
		echo "I won't support it"
	fi

	mkdir -p $serverPath/varnish
	echo "1.0" > $serverPath/varnish/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_varnish()
{
	rm -rf $serverPath/varnish
	echo "uninstall varnish" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_varnish
else
	Uninstall_varnish
fi
