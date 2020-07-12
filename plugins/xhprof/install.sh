#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

Install_xh()
{
	mkdir -p ${serverPath}/xhprof

	if [ ! -d ${serverPath}/xhprof/xhprof_lib ];then
		cp -rf $curPath/lib/* ${serverPath}/xhprof
	fi

	echo "${1}" > ${serverPath}/xhprof/version.pl
	echo '安装完成' > $install_tmp
		
}

Uninstall_xh()
{
	rm -rf ${serverPath}/xhprof
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_xh $2
else
	Uninstall_xh $2
fi
