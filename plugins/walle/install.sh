#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl


Install_walle()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/walle
	echo '1.0' > $serverPath/walle/version.pl

	if [ ! -f $serverPath/source/v2.0.1.tar.gz ];then
		wget -O $serverPath/source/v2.0.1.tar.gz https://github.com/meolu/walle-web/archive/v2.0.1.tar.gz
	fi

	if [ ! -d $serverPath/source/walle-web-2.0.1 ];then
		cd $serverPath/source && tar -zxvf v2.0.1.tar.gz
	fi

	if [ ! -d $serverPath/walle/code ];then
		mkdir -p $serverPath/walle/code
		cp -rf $serverPath/source/walle-web-2.0.1/* $serverPath/walle/code/
	fi

	cd $serverPath/walle/code && pip install -r $serverPath/walle/code/requirements/prod.txt

	echo '安装完成' > $install_tmp

}

Uninstall_walle()
{
	rm -rf $serverPath/walle
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_walle
else
	Uninstall_walle
fi