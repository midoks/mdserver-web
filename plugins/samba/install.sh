#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/bt_install.pl
Install_samba()
{
	echo '正在安装脚本文件...' > $install_tmp
	
	if [ $sysName == 'Darwin' ]; then
		echo 'The development machine is not open!!!' > $install_tmp
	else
		yum -y install samba*  cifs-utils
	fi
	
	mkdir -p $serverPath/samba
	echo '1.0' > $serverPath/samba/version.pl
	echo '安装完成' > $install_tmp

}

Uninstall_samba()
{
	rm -rf $serverPath/samba
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_samba
else
	Uninstall_samba
fi
