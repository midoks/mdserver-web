#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/bt_install.pl


Install_qbittorrent()
{
	if [ $sysName == 'Darwin' ]; then
		echo 'apple system'
	else
		yum -y install qt-devel boost-devel openssl-devel qt5-qtbase-devel qt5-linguist
	fi

	pip install python-qbittorrent

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/qbittorrent

	QB_DIR=${serverPath}/source/qbittorrent
	mkdir -p $QB_DIR

	if [ ! -f ${QB_DIR}/libtorrent-rasterbar-1.1.9.tar.gz ];then
		wget -O ${QB_DIR}/libtorrent-rasterbar-1.1.9.tar.gz https://github.com/arvidn/libtorrent/releases/download/libtorrent-1_1_9/libtorrent-rasterbar-1.1.9.tar.gz
	fi
	cd ${QB_DIR} && tar -zxf libtorrent-rasterbar-1.1.9.tar.gz
	cd ${QB_DIR} && cd libtorrent-rasterbar-1.1.9
	
	#修改为固定端口号
	#sed -i "s/i2p ? 1 : tracker_req().listen_port/8999/" src/http_tracker_connection.cpp
	./configure --prefix=$serverPath/lib/libtorrent CXXFLAGS=-std=c++11
	make && make install
	#echo "/www/server/lib/libtorrent/lib" > /etc/ld.so.conf.d/libtorrent-x86_64.conf
	echo "$serverPath/lib/libtorrent/lib" > /etc/ld.so.conf.d/libtorrent-x86_64.conf
	ldconfig
	#export LD_LIBRARY_PATH=/www/server/lib/libtorrent/lib
	#export CPLUS_INCLUDE_PATH=/www/server/lib/libtorrent/include/
	export CPLUS_INCLUDE_PATH=$serverPath/lib/libtorrent/include/
	export PKG_CONFIG_PATH=$serverPath/lib/libtorrent/lib/pkgconfig/


	if [ ! -f ${QB_DIR}/qbittorrent-4.1.5.tar.gz ];then
		wget -O ${QB_DIR}/qbittorrent-4.1.5.tar.gz https://github.com/qbittorrent/qBittorrent/archive/release-4.1.5.tar.gz
	fi

	cd ${QB_DIR} && tar -zxvf qbittorrent-4.1.5.tar.gz && \
	./configure --prefix=$serverPath/qbittorrent --disable-gui && make && make install

	echo '4.1.5' > $serverPath/qbittorrent/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_qbittorrent()
{
	rm -rf $serverPath/qbittorrent
	echo "Uninstall_qbittorrent" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_qbittorrent
else
	Uninstall_qbittorrent
fi
