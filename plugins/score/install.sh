#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")

install_tmp=${rootPath}'/tmp/bt_install.pl'

echo $curPath




download_Url=http://$nodeAddr:5880
Install_score()
{
	echo '正在安装脚本文件...' > $install_tmp
	
	# gcc /www/server/mdserver-web/plugin/score/testcpu.c -o /www/server/mdserver-web/plugin/score/testcpu -lpthread
	# if [ ! -f '/www/server/mdserver-web/plugin/score/testcpu' ];then
	# 	sleep 0.1
	# 	gcc /www/server/mdserver-web/plugin/score/testcpu.c -o /www/server/mdserver-web/plugin/score/testcpu -lpthread
	# fi
	
	
	echo '安装完成' > $install_tmp
}

Uninstall_score()
{
	echo '卸载完成' > $install_tmp
}


action=$1
echo $action
if [ "${1}" == 'install' ];then
	Install_score
else
	Uninstall_score
fi
