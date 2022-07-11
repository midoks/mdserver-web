#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


Install_pm2()
{
	echo '正在安装脚本文件...' > $install_tmp


	curl -o- http://npmjs.org/install.sh | bash
	
	if [ "$OSNAME" == 'debian' ] && [ "$OSNAME" == 'ubuntu' ];then
		apt install -y nodejs
		apt install -y pm2
	else 
		yum install -y nodejs
		npm install pm2 -g
	fi
	
	curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash

	mkdir -p $serverPath/pm2
	echo '1.0' > $serverPath/pm2/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_pm2()
{
	rm -rf $serverPath/pm2
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_pm2
else
	Uninstall_pm2
fi
