#!/bin/bash
PATH=/www/server/panel/pyenv/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

Install_App()
{
	pip install requests-oauthlib==1.3.0
	mkdir -p $serverPath/msonedrive
	echo '正在安装脚本文件...' > $install_tmp

	echo "${VERSION}" > $serverPath/msonedrive/version.pl
	echo '安装完成' > $install_tmp

	echo "Successify"
}


Uninstall_App()
{
	rm -rf $serverPath/msonedrive
}

if [ "${1}" == 'install' ];then
	Install_App
elif [ "${1}" == 'uninstall' ];then
	Uninstall_App
else
	echo 'Error!';
fi
