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

	if [ ! -d $serverPath/tmp/openresty.tar.gz ];then
		wget -O $serverPath/tmp/openresty.tar.gz https://openresty.org/download/openresty-1.13.6.2.tar.gz
	fi
	cd $serverPath/tmp && tar -zxvf openresty.tar.gz

	mkdir -p $serverPath/openresty
	cd $serverPath/tmp/openresty* && ./configure --prefix=$serverPath/openresty \
	--with-openssl=$serverPath/tmp/openssl-1.0.2q && make && make install
	
	echo '安装完成' > $install_tmp
}

Uninstall_openresty()
{
	rm -f $serverPath/openresty
	echo '卸载完成' > $install_tmp
}

action=$1
host=$2
if [ "${1}" == 'install' ];then
	Install_openresty
else
	Uninstall_openresty
fi
