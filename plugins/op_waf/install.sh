#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl


action=$1
version=$2

Install_of(){
	
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/op_waf

	echo "${version}" > $serverPath/op_waf/version.pl
	echo 'install ok' > $install_tmp

	cd ${rootPath} && python3 ${rootPath}/plugins/op_waf/index.py start
}

Uninstall_of(){

	cd ${rootPath} && python3 ${rootPath}/plugins/op_waf/index.py stop
	rm -rf $serverPath/op_waf
}


action=$1
if [ "${1}" == 'install' ];then
	Install_of
else
	Uninstall_of
fi
