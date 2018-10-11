#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

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
