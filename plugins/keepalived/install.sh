#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

# for mac
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/keepalived && bash install.sh install 2.2.8
# cd /www/server/mdserver-web/plugins/keepalived && bash install.sh install 2.2.8

# /www/server/keepalived/init.d/keepalived start

# systemctl status keepalived
# systemctl restart keepalived
# ifconfig

install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=$2

Install_App()
{
	echo '正在安装keepalived脚本文件...'
	mkdir -p $serverPath/source/keepalived

	if [ ! -f $serverPath/source/keepalived/keepalived-${VERSION}.tar.gz ];then
		wget -O $serverPath/source/keepalived/keepalived-${VERSION}.tar.gz https://keepalived.org/software/keepalived-${VERSION}.tar.gz
	fi

	#检测文件是否损坏.
	md5_file_ok=8c26f75a8767e5341d82696e1e717115
	if [ -f $serverPath/source/keepalived/keepalived-${VERSION}.tar.gz ];then
		md5_file=`md5sum $serverPath/source/keepalived/keepalived-${VERSION}.tar.gz  | awk '{print $1}'`
		if [ "${md5_file}" != "${md5_file_ok}" ]; then
			echo "keepalived-${version} 下载文件不完整,重新安装"
			rm -rf $serverPath/source/keepalived/keepalived-${VERSION}.tar.gz
		fi
	fi
	
	echo $serverPath/keepalived/keepalived-${VERSION}
	if [ -d $serverPath/keepalived/keepalived-${VERSION} ];then
		cd  $serverPath/keepalived/keepalived-${VERSION}
	else 
		cd $serverPath/source/keepalived && tar -zxvf keepalived-${VERSION}.tar.gz
		cd  $serverPath/keepalived/keepalived-${VERSION}
	fi

	cd $serverPath/source/keepalived/keepalived-${VERSION}

	./configure --prefix=$serverPath/keepalived && make && make install

	# for test
	# mkdir -p $serverPath/keepalived
	if [ -d $serverPath/keepalived ];then
		echo "${VERSION}" > $serverPath/keepalived/version.pl
		echo 'keepalived安装完成'

		cd ${rootPath} && python3 ${rootPath}/plugins/keepalived/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/keepalived/index.py initd_install
	fi

	if [ -d $serverPath/source/keepalived/keepalived-${VERSION} ];then
		rm -rf $serverPath/source/keepalived/keepalived-${VERSION}
	fi
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/keepalived.service ];then
		systemctl stop keepalived
		systemctl disable keepalived
		rm -rf /usr/lib/systemd/system/keepalived.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/keepalived.service ];then
		systemctl stop keepalived
		systemctl disable keepalived
		rm -rf /lib/systemd/system/keepalived.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/keepalived/initd/keepalived ];then
		$serverPath/keepalived/initd/keepalived stop
	fi

	rm -rf $serverPath/keepalived
	echo "keepalived卸载完成"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
