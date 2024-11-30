#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sys_os=`uname`
VERSION=1.6.32

echo $sys_os

Install_mem(){
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/memcached
	echo '正在安装脚本文件...'

	if [ ! -f $serverPath/source/memcached.tar.gz ];then
		wget  --no-check-certificate -O $serverPath/source/memcached/memcached.tar.gz https://www.memcached.org/files/memcached-${VERSION}.tar.gz
	fi
	
	cd $serverPath/source/memcached && tar -zxvf memcached.tar.gz

	OPTIONS=''
	if [ ${sys_os} == "Darwin" ]; then
		LIB_DEPEND_DIR=`brew info libevent | grep /opt/homebrew/Cellar/libevent | cut -d \  -f 1 | awk 'END {print}'`
		OPTIONS="${OPTIONS} --with-libevent=${LIB_DEPEND_DIR}"
	fi

	echo "./configure --prefix=${serverPath}/memcached && make && make install"
	cd $serverPath/source/memcached/memcached-${VERSION}
	./configure --prefix=$serverPath/memcached \
	$OPTIONS

	make && make install

	if [ -d $serverPath/memcached ];then
		echo '1.6' > $serverPath/memcached/version.pl
		echo '安装memcached成功'

		cd ${rootPath} && python3 ${rootPath}/plugins/memcached/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/memcached/index.py initd_install

		rm -rf $serverPath/source/memcached/memcached-${VERSION}
	fi
}

Uninstall_mem()
{

	if [ -f /usr/lib/systemd/system/memcached.service ];then
		systemctl stop memcached
		systemctl disable memcached
		rm -rf /usr/lib/systemd/system/memcached.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/memcached/initd/memcached ];then
		$serverPath/memcached/initd/memcached stop
	fi
	rm -rf $serverPath/memcached
	echo '卸载memcached成功'
}


# /www/server/memcached/bin/memcached -d -p 11211 -u root  -m 100 -c 100

action=$1
if [ "${1}" == 'install' ];then
	Install_mem
else
	Uninstall_mem
fi
