#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl

Install_gae()
{
	mkdir -p ${serverPath}/gae
	mkdir -p ${serverPath}/source/gae
	
	os=`uname`
	if [ "Darwin" == "$os" ];then
		file=google-cloud-sdk-218.0.0-darwin-x86_64.tar.gz
	else
		file=google-cloud-sdk-218.0.0-linux-x86_64.tar.gz
	fi

	if [ ! -f $serverPath/source/gae/$file ];then
		wget -O $serverPath/source/gae/$file https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/$file
	fi

	if [ ! -d $serverPath/source/gae/google-cloud-sdk ];then
		cd $serverPath/source/gae && tar zxvf $file
	fi

	cp -r $serverPath/source/gae/google-cloud-sdk ${serverPath}/gae



	echo "${1}" > ${serverPath}/gae/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_gae()
{
	rm -rf ${serverPath}/gae
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_gae $2
else
	Uninstall_gae $2
fi
