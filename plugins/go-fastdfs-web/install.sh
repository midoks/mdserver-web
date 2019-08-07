#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl

action=$1
version=$2
Install_gf()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/go-fastdfs-web
	FF_DIR=${serverPath}/go-fastdfs-web
	cd $FF_DIR

	if [ $sysName == 'Darwin' ]; then
		FF_SS_DIR=${serverPath}/source/go-fastdfs-web
		mkdir -p $FF_SS_DIR
		if [ ! -f $FF_SS_DIR/go-fastdfs-web-1.1.2.tar.gz ]; then
			wget -O $FF_SS_DIR/go-fastdfs-web-1.1.2.tar.gz https://github.com/perfree/go-fastdfs-web/releases/download/1.1.2/go-fastdfs-web-1.1.2.tar.gz
		fi

		cd $FF_SS_DIR
		if [ ! -d  $FF_SS_DIR/go-fastdfs-web ]; then
			tar -zxvf $FF_SS_DIR/go-fastdfs-web-1.1.2.tar.gz
		fi

		if [ ! -d $FF_DIR/config ];then
			cp -rf $FF_SS_DIR/go-fastdfs-web/* $FF_DIR/
		fi
	fi
	
	echo "$version" > $FF_DIR/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_gf()
{
	rm -rf $serverPath/go-fastdfs-web
	echo "卸载完成" > $install_tmp
}


if [ "${1}" == 'install' ];then
	Install_gf $version
else
	Uninstall_gf $version
fi
