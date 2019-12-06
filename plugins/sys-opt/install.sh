#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl


Install_sysopt()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/sys-opt
	echo '1.0' > $serverPath/sys-opt/version.pl
	echo '安装完成' > $install_tmp

}

Uninstall_sysopt()
{
	rm -rf $serverPath/sys-opt
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_sysopt
else
	Uninstall_sysopt
fi
