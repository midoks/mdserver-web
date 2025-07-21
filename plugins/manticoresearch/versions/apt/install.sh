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
	source ${rootPath}/bin/activate
fi

VERSION=$2

Install_App()
{
	echo '正在安装manticoresearch...'
	mkdir -p $serverPath/manticoresearch

	MC_DIR=${serverPath}/source/manticoresearch
	mkdir -p $MC_DIR

	wget --no-check-certificate -O $MC_DIR/manticore-repo.noarch.deb https://repo.manticoresearch.com/manticore-repo.noarch.deb
	dpkg -i $MC_DIR/manticore-repo.noarch.deb
	apt update -y 
	apt -y install manticore manticore-extra


	echo "${VERSION}" > $serverPath/manticoresearch/version.pl


	cd ${rootPath} && python3 plugins/manticoresearch/index.py start ${VERSION}
	cd ${rootPath} && python3 plugins/manticoresearch/index.py initd_install ${VERSION}

	if [ -d ${MC_DIR} ];then
		rm -rf ${MC_DIR}
	fi
}

Uninstall_App()
{
	cd ${rootPath} && python3 plugins/manticoresearch/index.py stop ${VERSION}
	cd ${rootPath} && python3 plugins/manticoresearch/index.py initd_uninstall ${VERSION}

	apt -y remove manticore manticore-extra
	apt -y autoremove

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

	echo "卸载manticoresearch成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
