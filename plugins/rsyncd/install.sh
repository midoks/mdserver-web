#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/bt_install.pl
Install_rsyncd()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/rsyncd
	echo '1.0' > $serverPath/rsyncd/version.pl
	echo '安装完成' > $install_tmp

}

Uninstall_rsyncd()
{
	rm -rf $serverPath/rsyncd
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_rsyncd
else
	Uninstall_rsyncd
fi
