#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
sys_os=`uname`


Install_App()
{
	mkdir -p ${serverPath}/backup_ftp
	echo "${1}" > ${serverPath}/backup_ftp/version.pl
	echo '安装完成' > $install_tmp

}

Uninstall_App()
{
	rm -rf ${serverPath}/backup_ftp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App $2
else
	Uninstall_App $2
fi
