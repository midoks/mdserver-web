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
	wget -O $serverPath/tmp/csvn.tar.xz https://github.com/midoks/mdserver-web/releases/download/init/CollabNetSubversionEdge-5.1.4_linux-x86_64.tar.xz

	cd $serverPath/tmp && tar -Jxf $serverPath/tmp/csvn.tar.xz
	mkdir -p $serverPath/csvn
	mv $serverPath/tmp/csvn $serverPath/csvn/5.1
	
	echo '安装完成' > $install_tmp

	rm -rf $serverPath/tmp
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
