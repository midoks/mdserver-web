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
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
	OSNAME='raspbian'
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
		apt-get install varnish -y
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
