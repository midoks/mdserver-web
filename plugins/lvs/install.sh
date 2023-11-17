#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
sys_os=`uname`
VERSION=1.6.22

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/lvs && bash install.sh install 1.0
# cd /www/server/mdserver-web/plugins/lvs && bash install.sh install 1.0


Install_LVS(){
	mkdir -p $serverPath/source

	which ipvsadm
	if [ "$?" == "0" ];then
		echo '已安装LVS!!'
		exit 0
	fi

	echo '正在安装LVS...'

	# 检测平台命令
	which apt
	if [ "$?" == "0" ];then
		apt install -y ipvsadm
	fi

	which yum
	if [ "$?" == "0" ];then
		yum install -y ipvsadm
	fi

	which ipvsadm
	if [ "$?" == "0" ];then
		echo '正在安装LVS成功!'
		mkdir -p $serverPath/lvs

		ipv_version=`ipvsadm -v | awk '{print $2}'`
		if [ "$ipv_version" != "" ];then
			echo "$ipv_version" > $serverPath/lvs/version.pl
		else
			echo '1.0' > $serverPath/lvs/version.pl
		fi

		cd ${rootPath} && python3 ${rootPath}/plugins/lvs/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/lvs/index.py initd_install
	else
		echo '正在安装LVS失败!'
	fi
}

Uninstall_LVS()
{
	# 检测平台命令
	which apt
	if [ "$?" == "0" ];then
		apt remove -y ipvsadm
	fi

	which yum
	if [ "$?" == "0" ];then
		yum uninstall -y ipvsadm
	fi
	echo "卸载LVS完成"

	if [ -d $serverPath/lvs ];then
		rm -rf $serverPath/lvs
	fi
}

action=$1
if [ "${1}" == 'install' ];then
	Install_LVS
else
	Uninstall_LVS
fi
