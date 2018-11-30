#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/bt_install.pl

Install_readme()
{
	mkdir -p ${serverPath}/readme
	echo "${1}" > ${serverPath}/readme/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_readme()
{
	rm -rf ${serverPath}/readme
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_readme $2
else
	Uninstall_readme $2
fi
