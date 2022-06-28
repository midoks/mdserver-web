#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

if id www &> /dev/null ;then 
    echo "www UID is `id -u www`"
    echo "www Shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	# useradd -g www -s /sbin/nologin www
	useradd -g www -s /bin/bash www
fi

action=$1
type=$2

if [ "${2}" == "" ];then
	echo '缺少安装脚本...' > $install_tmp
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...' > $install_tmp
	exit 0
fi

if [ "${action}" == "uninstall" ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php/index.py stop ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php/index.py initd_uninstall ${type}

	if [ -f /lib/systemd/system/php${type}.service ];then
		systemctl stop php${type}
		rm -rf /lib/systemd/system/php${type}.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" =="install" ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php/index.py initd_install ${type}
fi


