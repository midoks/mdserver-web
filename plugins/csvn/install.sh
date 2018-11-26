#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl

Install_csvn()
{
	mkdir -p $serverPath/tmp

	echo '正在安装脚本文件...' > $install_tmp

	if [ ! -d $serverPath/tmp/csvn.tar.xz ];then
		wget -O $serverPath/tmp/csvn.tar.xz https://github.com/midoks/mdserver-web/releases/download/init/CollabNetSubversionEdge-5.1.4_linux-x86_64.tar.xz
	fi

	cd $serverPath/tmp && tar -Jxf $serverPath/tmp/csvn.tar.xz
	mv $serverPath/tmp/csvn $serverPath/csvn
	
	echo '安装完成' > $install_tmp
}

Uninstall_csvn()
{
	rm -rf $serverPath/csvn
}


action=$1
host=$2
if [ "${1}" == 'install' ];then
	Install_csvn
else
	Uninstall_csvn
fi
