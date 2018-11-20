#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

Install_nginx()
{
	echo "Install_safelogin"
}

Uninstall_nginx()
{
	echo "Uninstall_safelogin"
}

action=$1
host=$2;
if [ "${1}" == 'install' ];then
	Install_nginx
else
	Uninstall_nginx
fi
