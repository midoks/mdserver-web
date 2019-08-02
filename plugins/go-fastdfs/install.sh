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
	mkdir -p $serverPath/go-fastdfs
	FF_DIR=${serverPath}/go-fastdfs
	cd $FF_DIR

	if [ $sysName == 'Darwin' ]; then
		FF_SS_DIR=${serverPath}/source/go-fastdfs
		mkdir -p $FF_SS_DIR
		if [ ! -f $FF_SS_DIR/v1.3.1.tar.gz ]; then
			wget -O $FF_SS_DIR/v1.3.1.tar.gz https://github.com/sjqzhang/go-fastdfs/archive/v1.3.1.tar.gz
		fi

		if [ ! -d $FF_SS_DIR/go-fastdfs-1.3.1 ]; then
			cd $FF_SS_DIR && tar -zxvf $FF_SS_DIR/v1.3.1.tar.gz
		fi


		cd $FF_SS_DIR/go-fastdfs-1.3.1

		if [ -d $FF_SS_DIR/go-fastdfs-1.3.1/vendor ];then
			 mv vendor src
		fi

		if [ ! -f $FF_SS_DIR/go-fastdfs-1.3.1/fileserver ]; then
			pwd=`pwd`
			echo "$pwd go build -o fileserver fileserver.go"
			GOPATH=$pwd go build -o fileserver fileserver.go
		fi

		if [ ! -f $FF_DIR/fileserver ];then
			cp -f fileserver $FF_DIR

			cd $FF_DIR
		fi
		


	else
		cd $FF_DIR
		if [ ! -f ${FF_DIR}/fileserver ];then
			wget --no-check-certificate  https://github.com/sjqzhang/go-fastdfs/releases/download/v1.3.1/fileserver -O fileserver
			chmod +x fileserver
		fi
	fi

	
	echo "$version" > $serverPath/go-fastdfs/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_gf()
{
	rm -rf $serverPath/go-fastdfs
	echo "卸载完成" > $install_tmp
}


if [ "${1}" == 'install' ];then
	Install_gf $version
else
	Uninstall_gf $version
fi
