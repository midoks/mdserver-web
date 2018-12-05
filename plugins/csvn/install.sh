#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl


CSVN_SOURCE='https://github.com/midoks/mdserver-web/releases/download/init/CollabNetSubversionEdge-5.1.4_linux-x86_64.tar.xz'

Install_csvn()
{
	mkdir -p $serverPath/source

	echo '正在安装脚本文件...' > $install_tmp

	if [ ! -f $serverPath/source/csvn.tar.xz ];then
		wget -O $serverPath/source/csvn.tar.xz ${CSVN_SOURCE}
	fi

	cd $serverPath/source && tar -Jxf $serverPath/source/csvn.tar.xz
	mv $serverPath/source/csvn $serverPath/csvn
	echo '5.1' > $serverPath/csvn/version.pl


	if id -u csvn > /dev/null 2>&1; then
        echo "csvn user exists"
	else
		useradd csvn
		cp /etc/sudoers{,.`date +"%Y-%m-%d_%H-%M-%S"`}
		echo "csvn ALL=(ALL)      ALL" >> /etc/sudoers
	fi

	chown -R  csvn:csvn $serverPath/csvn
	
	$serverPath/csvn/bin/csvn start
	$serverPath/csvn/bin/csvn-httpd start
	
	echo '安装完成' > $install_tmp
}

Uninstall_csvn()
{
	rm -rf $serverPath/csvn
}


action=$1
host=$2
if [ "${1}" == 'install' ];then
	Install_csvn
else
	Uninstall_csvn
fi
