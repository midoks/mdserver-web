#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2


sysName=`uname`
echo "use system: ${sysName}"

if [ ${sysName} == "Darwin" ]; then
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

Install_app()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/supervisor
	mkdir -p $serverPath/supervisor/log
	mkdir -p $serverPath/supervisor/run

	echo 'supervisor install...'
	if [ "centos" == "$OSNAME" ] || [ "fedora" == "$OSNAME" ];then
    	# yum install supervisor -y
    	pip install  supervisor
    elif [ "ubuntu" == "$OSNAME" ] || [ "debian" == "$OSNAME" ] ;then
    	# apt install supervisor -y 
    	pip install  supervisor
	else
		pip install  supervisor
    	# brew install supervisor
	fi

	echo "${VERSION}" > $serverPath/supervisor/version.pl
	echo '安装完成[supervisor]' > $install_tmp
}

Uninstall_app()
{
	rm -rf $serverPath/supervisor

	if [ -f /lib/systemd/system/supervisor.service ];then
		rm -rf /lib/systemd/system/supervisor.service
	fi

	echo "卸载完成[supervisor]" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app
else
	Uninstall_app
fi
