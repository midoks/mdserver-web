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
Install_solr()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/go-fastfds
	FF_DIR=${serverPath}/go-fastfds
	cd $FF_DIR

	if [ $sysName == 'Darwin' ]; then
		FF_SS_DIR=${serverPath}/source/go-fastfds
		mkdir -p $FF_SS_DIR
		if [ ! -f $FF_SS_DIR/go-fastdfs/v1.3.1.tar.gz ]; then
			wget -O $FF_SS_DIR/go-fastdfs/v1.3.1.tar.gz   https://github.com/sjqzhang/go-fastdfs/archive/v1.3.1.tar.gz
		fi

		if [ ! -d $FF_SS_DIR/go-fastdfs/go-fastdfs-1.3.1 ]; then
			cd $FF_SS_DIR/go-fastdfs && tar -zxvf $FF_SS_DIR/go-fastdfs/v1.3.1.tar.gz
		fi


	else
		if [ ! -f ${FF_DIR}/fileserver ];then
			wget --no-check-certificate  https://github.com/sjqzhang/go-fastdfs/releases/download/v1.3.1/fileserver -O fileserver
		fi
	fi

	
	echo "$version" > $serverPath/solr/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_solr()
{
	rm -rf $serverPath/go-fastfds
	echo "卸载完成" > $install_tmp
}


if [ "${1}" == 'install' ];then
	Install_solr $version
else
	Uninstall_solr $version
fi
