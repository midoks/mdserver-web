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
sys_os=`uname`

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

if [ "$sys_os" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

Install_App(){
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/op_load_balance
	echo "${version}" > $serverPath/op_load_balance/version.pl
	cd ${rootPath} && python3 ${rootPath}/plugins/op_load_balance/index.py start
	echo 'install ok' > $install_tmp
}

Uninstall_App(){
	cd ${rootPath} && python3 ${rootPath}/plugins/op_load_balance/index.py stop
	rm -rf $serverPath/op_load_balance
}


action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
