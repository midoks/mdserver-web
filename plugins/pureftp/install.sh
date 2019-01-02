#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl

Install_pureftp()
{
	mkdir -p ${serverPath}/pureftp
	mkdir -p ${serverPath}/source/pureftp

	VER=$1
	FILE=pure-ftpd-${VER}.tar.gz
	FDIR=pure-ftpd-${VER}
	DOWNLOAD=https://download.pureftpd.org/pub/pure-ftpd/releases/pure-ftpd-${VER}.tar.gz
	

	if [ ! -f $serverPath/source/pureftp/$FILE ];then
		wget -O $serverPath/source/pureftp/$FILE $DOWNLOAD
	fi

	if [ ! -d $serverPath/source/pureftp/$FDIR ];then
		cd $serverPath/source/pureftp  && tar zxvf $FILE
	fi

	cd $serverPath/source/pureftp/$FDIR &&  ./configure --prefix=${serverPath}/pureftp \
　　 	--with-everything && make && make install && make clean
	
	echo "${1}" > ${serverPath}/pureftp/version.pl
	echo '安装完成' > $install_tmp
	

	
}

Uninstall_pureftp()
{
	rm -rf ${serverPath}/pureftp
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_pureftp $2
else
	Uninstall_pureftp $2
fi
