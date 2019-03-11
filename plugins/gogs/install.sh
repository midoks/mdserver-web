#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl


GOGS_DOWNLOAD='https://dl.gogs.io'

getOs(){
	os=`uname`
	if [ "Darwin" == "$os" ];then
		echo 'darwin'
	else
		echo 'linux'
	fi
	return 0
}

getBit(){
	echo `getconf  LONG_BIT`
}


Install_gogs()
{
	mkdir -p $serverPath/source/gogs

	echo '正在安装脚本文件...' > $install_tmp
	version=$1
	os=`getOs`

	if [ "darwin" == "$os" ];then
		file=gogs_${version}_darwin_amd64.zip
	else
		file=gogs_${version}_linux_amd64.zip
	fi

	if [ ! -f $serverPath/source/gogs/$file ];then
		wget -O $serverPath/source/gogs/$file ${GOGS_DOWNLOAD}/${version}/${file}
	fi

	cd $serverPath/source/gogs && unzip -o $file -d gogs_${version}
	mv $serverPath/source/gogs/gogs_${version}/gogs/ $serverPath/gogs
	echo $version > $serverPath/gogs/version.pl

	if id -u gogs > /dev/null 2>&1; then
        echo "csvn user exists"
	else
		useradd gogs
		cp /etc/sudoers{,.`date +"%Y-%m-%d_%H-%M-%S"`}
		echo "gogs ALL=(ALL)    NOPASSWD: ALL" >> /etc/sudoers
	fi

	echo 'install success' > $install_tmp
}

Uninstall_gogs()
{
	rm -rf $serverPath/gogs
	echo 'uninstall success' > $install_tmp
}


action=$1
version=$2
if [ "${1}" == 'install' ];then
	Install_gogs $version
else
	Uninstall_gogs $version
fi
