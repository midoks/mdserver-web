#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl
SYSOS=`uname`

Install_socket5()
{
	yum -y install gcc automake make pam-devel openldap-devel cyrus-sasl-devel

	isStart=""
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/socket5

	if [ ! -f $serverPath/source/ss5-3.8.9-8.tar.gz ];then
		wget -O $serverPath/source/ss5-3.8.9-8.tar.gz http://downloads.sourceforge.net/project/ss5/ss5/3.8.9-8/ss5-3.8.9-8.tar.gz
	fi
	echo '1.0' > $serverPath/socket5/version.pl

	cd $serverPath/source && tar -xzvf ss5-3.8.9-8.tar.gz
	cd $serverPath/source/ss5-3.8.9 && ./configure && make && make install

	echo 'install complete' > $install_tmp
}

Uninstall_socket5()
{
	rm -rf $serverPath/socket5
	rm -rf /usr/sbin/ss5
	service ss5 stop
	rm -rf /etc/init.d/ss5
	echo "Uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_socket5
else
	Uninstall_socket5
fi
