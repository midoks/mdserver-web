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
	mkdir -p $zimgSourceDir/libjpeg-turbo
	cd $zimgSourceDir/libjpeg-turbo
	if [ ! -d $zimgSourceDir/libjpeg-turbo ];then
		wget https://downloads.sourceforge.net/project/libjpeg-turbo/1.3.1/libjpeg-turbo-1.3.1.tar.gz
		tar zxvf libjpeg-turbo-1.3.1.tar.gz
		cd libjpeg-turbo-1.3.1
		./configure --prefix=/usr/local --with-jpeg8
		make && make install
	fi 
}

Install_zimg_source(){
	mkdir -p $zimgSourceDir
	cd $zimgSourceDir
	if [ ! -d $zimgSourceDir/zimg ];then
		git clone https://github.com/buaazp/zimg -b master --depth=1
		cd zimg
		make
	fi
	if [ -f $zimgSourceDir/zimg/bin/zimg ];then
		cp -r $zimgSourceDir/zimg/bin $serverPath/zimg
	fi
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
		if [ ! -f $serverPath/zimg/bin ];then
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
