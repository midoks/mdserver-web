#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl

Install_safelogin()
{
	mkdir -p /www/server/panel/plugin/safelogin
	echo '正在安装脚本文件...' > $install_tmp
	wget -O /www/server/panel/plugin/safelogin/safelogin_main.py $download_Url/install/lib/plugin/safelogin/safelogin_main.py -T 5
	wget -O /www/server/panel/plugin/safelogin/index.html $download_Url/install/lib/plugin/safelogin/index.html -T 5
	wget -O /www/server/panel/plugin/safelogin/info.json $download_Url/install/lib/plugin/safelogin/info.json -T 5
	wget -O /www/server/panel/plugin/safelogin/icon.png $download_Url/install/lib/plugin/safelogin/icon.png -T 5
	echo '安装完成' > $install_tmp
	
}

Uninstall_safelogin()
{
	chattr -i /www/server/panel/plugin/safelogin/token.pl
	rm -f /www/server/panel/data/limitip.conf
	sed -i "/ALL/d" /etc/hosts.deny
	rm -rf /www/server/panel/plugin/safelogin
}


action=$1
type=$2

if [ "${2}" == "" ];then
	echo '缺少安装脚本...' > $install_tmp
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...' > $install_tmp
	exit 0
fi

sh -x $curPath/versions/$2/install.sh $1
