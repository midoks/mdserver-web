#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=1.6.15

Install_mem(){
	mkdir -p $serverPath/source
	echo '正在安装脚本文件...' > $install_tmp

	if [ ! -f $serverPath/source/memcached.tar.gz ];then
		wget -O $serverPath/source/memcached.tar.gz http://www.memcached.org/files/memcached-${VERSION}.tar.gz
	fi
	
	cd $serverPath/source && tar -zxvf memcached.tar.gz

	mkdir -p $serverPath/memcached
	echo "./configure --prefix=${serverPath}/memcached && make && make install"
	cd $serverPath/source/memcached-${VERSION} && ./configure --prefix=$serverPath/memcached && make && make install

	echo '1.6' > $serverPath/memcached/version.pl
	echo 'install ok' > $install_tmp
}

Uninstall_mem()
{
	${serverPath}/memcached/init.d/memcached stop
	rm -rf $serverPath/memcached
}


action=$1
if [ "${1}" == 'install' ];then
	Install_mem
else
	Uninstall_mem
fi
