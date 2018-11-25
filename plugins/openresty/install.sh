#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl


Install_openresty()
{
	mkdir -p $serverPath/tmp
	echo '正在安装脚本文件...' > $install_tmp

	wget -O $serverPath/tmp/openresty.tar.gz https://openresty.org/download/openresty-1.13.6.2.tar.gz
	cd $serverPath/tmp && tar -zxvf openresty.tar.gz

	mkdir -p $serverPath/openresty
	cd openresty* && ./configure --prefix=$serverPath/openresty && make && make install
	
	echo '安装完成' > $install_tmp
	#rm -rf $serverPath/tmp
}

Uninstall_openresty()
{
	echo "Uninstall_safelogin"
}

action=$1
host=$2
if [ "${1}" == 'install' ];then
	Install_openresty
else
	Uninstall_openresty
fi
