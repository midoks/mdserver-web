#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

# cd /www/server/mdserver-web && . ./bin/activate && python3 plugins/memcached/index.py upgrade_check 1.6

action=$1

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sys_os=`uname`
VERSION=1.6.45

echo $sys_os

Install_mem(){
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/memcached
	echo '正在安装脚本文件...'

	if [ ! -f $serverPath/source/memcached.tar.gz ];then
		wget --no-check-certificate -O $serverPath/source/memcached/memcached.tar.gz https://www.memcached.org/files/memcached-${VERSION}.tar.gz
	fi
	
	cd $serverPath/source/memcached && tar -zxvf memcached.tar.gz

	OPTIONS=''
	if [ ${sys_os} = "Darwin" ]; then
		LIB_DEPEND_DIR=`brew --prefix libevent`
		OPTIONS="${OPTIONS} --with-libevent=${LIB_DEPEND_DIR}"
		OPTIONS="${OPTIONS} --disable-docs"

		#mac 新版问题，后续可能会解决
		echo "cat ${rootPath}/plugins/memcached/hook/darwin_priv.c > $serverPath/source/memcached/memcached-${VERSION}/darwin_priv.c"
		cat ${rootPath}/plugins/memcached/hook/darwin_priv.c > $serverPath/source/memcached/memcached-${VERSION}/darwin_priv.c
	fi

	echo "./configure --prefix=${serverPath}/memcached && make && make install"
	cd $serverPath/source/memcached/memcached-${VERSION}
	./configure --prefix=$serverPath/memcached \
	$OPTIONS

	make && make install

	if [ -d $serverPath/memcached ] || [ "$action" == "upgrade" ];then
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
if [ "${1}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_mem
elif [ "${1}" = 'uninstall' ];then
	Uninstall_mem
else
	echo "OPTIONS ERROR"
fi