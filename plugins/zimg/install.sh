#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


zimgSourceDir=${serverPath}/source/zimg

install_tmp=${rootPath}/tmp/mw_install.pl

SYSOS=`uname`

Install_libjpeg_turbo(){
	mkdir -p $zimgSourceDir/zimg/libjpeg-turbo
	cd $zimgSourceDir/zimg/libjpeg-turbo
	wget https://downloads.sourceforge.net/project/libjpeg-turbo/1.3.1/libjpeg-turbo-1.3.1.tar.gz
	tar zxvf libjpeg-turbo-1.3.1.tar.gz
	cd libjpeg-turbo-1.3.1
	./configure --prefix=/usr/local --with-jpeg8
	make && make install
}

Install_zimg_source(){
	mkdir -p $zimgSourceDir/zimg
	cd $zimgSourceDir/zimg
	git clone https://github.com/buaazp/zimg -b master --depth=1
	cd zimg
	make
}

Install_zimg()
{
	isStart=""
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/zimg
	echo '1.0' > $serverPath/zimg/version.pl

	if [ "Darwin" == "$SYSOS" ];then
		echo 'macosx unavailable' > $install_tmp
	else
		if [ ! -f $serverPath/zimg/zimg ];then
			yum install nasm -y
			Install_libjpeg_turbo
			Install_zimg_source
		fi
	fi

	echo 'Install complete' > $install_tmp
}

Uninstall_zimg()
{
	rm -rf $serverPath/zimg
	echo "Uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_zimg
else
	Uninstall_zimg
fi
