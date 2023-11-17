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
# cd /wwww/mdserver-web/plugins/lvs && bash install.sh install 1.0


Install_LVS(){
	mkdir -p $serverPath/source
	# mkdir -p $serverPath/memcached
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

	if [ -d $serverPath/lvs ];then
		echo '1.6' > $serverPath/lvs/version.pl
		echo '正在安装LVS成功!'

		cd ${rootPath} && python3 ${rootPath}/plugins/lvs/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/lvs/index.py initd_install
	fi
}

Uninstall_LVS()
{

	# if [ -f /usr/lib/systemd/system/memcached.service ];then
	# 	systemctl stop memcached
	# 	systemctl disable memcached
	# 	rm -rf /usr/lib/systemd/system/memcached.service
	# 	systemctl daemon-reload
	# fi

	# if [ -f $serverPath/memcached/initd/memcached ];then
	# 	$serverPath/memcached/initd/memcached stop
	# fi
	echo "卸载LVS完成"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_LVS
else
	Uninstall_LVS
fi
