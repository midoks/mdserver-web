#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sys_os=`uname`
Install_xh()
{
	mkdir -p ${serverPath}/xhprof

	if [ ! -d ${serverPath}/xhprof/xhprof_lib ];then
		cp -rf $curPath/lib/* ${serverPath}/xhprof
	fi

	echo "${1}" > ${serverPath}/xhprof/version.pl
	echo '安装完成'

	if [ "$sys_os" != "Darwin" ];then
		cd $rootPath && python3 ${rootPath}/plugins/xhprof/index.py start
	fi	
}

Uninstall_xh()
{
	if [ "$sys_os" != "Darwin" ];then
		cd $rootPath && python3 ${rootPath}/plugins/xhprof/index.py stop
	fi	

	rm -rf ${serverPath}/xhprof
	cd /tmp/xhprof && rm -rf *.xhprof

	if [ -f ${serverPath}/web_conf/nginx/vhost/xhprof.conf ];then
		rm -f ${serverPath}/web_conf/nginx/vhost/xhprof.conf
	fi
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_xh $2
else
	Uninstall_xh $2
fi
