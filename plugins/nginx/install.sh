#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'
public_file=/www/server/panel/install/public.sh
if [ ! -f $public_file ];then
	wget -O $public_file http://download.bt.cn/install/public.sh -T 5;
fi
. $public_file

download_Url=$NODE_URL

Install_safelogin()
{
	echo "Install_safelogin"
}

Uninstall_safelogin()
{
	echo "Uninstall_safelogin"
}

action=$1
host=$2;
if [ "${1}" == 'install' ];then
	Install_safelogin
else
	Uninstall_safelogin
fi
