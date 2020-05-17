#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl

pip install pygeoip
pip install pytz

Install_dht()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/simdht
	echo '1.0' > $serverPath/simdht/version.pl
	echo '安装完成' > $install_tmp

}

Uninstall_dht()
{
	rm -rf $serverPath/simdht
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_dht
else
	Uninstall_dht
fi
