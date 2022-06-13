#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4
# cd /www/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4

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

Install_app_mac()
{

	if [ ! -f $serverPath/source/mongodb-macos-x86_64-${VERSION}.tgz ];then
		wget -O $serverPath/source/mongodb-macos-x86_64-${VERSION}.tgz https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-${VERSION}.tgz
	fi

	cd $serverPath/source && tar -zxvf mongodb-macos-x86_64-${VERSION}.tgz
	
	cd  mongodb-macos-x86_64-${VERSION} && mv  ./* $serverPath/mongodb
}


# https://repo.mongodb.org/yum/redhat/7/mongodb-org/5.0/x86_64/RPMS/mongodb-org-server-5.0.4-1.el7.x86_64.rpm
Install_app_linux(){
	if [ ! -f $serverPath/source/mongodb-org-server-${VERSION}-1.el7.x86_64.rpm ];then
		wget -O $serverPath/source/mongodb-org-server-${VERSION}-1.el7.x86_64.rpm https://repo.mongodb.org/yum/redhat/7/mongodb-org/5.0/x86_64/RPMS/mongodb-org-server-${VERSION}-1.el7.x86_64.rpm
	fi
	
	rpm -ivh $serverPath/source/mongodb-org-server-${VERSION}-1.el7.x86_64.rpm 
}


Install_app()
{
	pip3 install pymongo

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/mongodb

	if [ "macos" == "$OSNAME" ];then
		Install_app_mac
	elif [ "ubuntu" == "$OSNAME" ] || [ "debian" == "$OSNAME" ] ;then
		apt install -y mongodb
	else
		Install_app_linux
	fi

	echo "${VERSION}" > $serverPath/mongodb/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_app()
{
	# apt remove mongodb -y
	rm -rf $serverPath/mongodb
	echo "Uninstall_mongodb" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app
else
	Uninstall_app
fi
