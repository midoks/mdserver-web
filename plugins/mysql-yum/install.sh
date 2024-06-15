#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


# cd /www/server/mdserver-web/plugins/mysql-yum && bash install.sh install 8.4
# cd /www/server/mdserver-web/plugins/mysql-yum && bash install.sh uninstall 8.0
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql-yum/index.py start 8.0
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql-yum/index.py get_master_status 8.4

install_tmp=${rootPath}/tmp/mw_install.pl


action=$1
type=$2

if id mysql &> /dev/null ;then 
    echo "mysql UID is `id -u mysql`"
    echo "mysql Shell is `grep "^mysql:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd mysql
	useradd -g mysql -s /usr/sbin/nologin mysql
fi



if [ "${2}" == "" ];then
	echo '缺少安装脚本...' > $install_tmp
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...' > $install_tmp
	exit 0
fi

if [ "${action}" == "uninstall" ];then
	
	cd ${rootPath} && python3 plugins/mysql-yum/index.py stop ${type}
	cd ${rootPath} && python3 plugins/mysql-yum/index.py initd_uninstall ${type}
	cd $curPath

	if [ -f /usr/lib/systemd/system/mysql-yum.service ] || [ -f /lib/systemd/system/mysql-yum.service ];then
		systemctl stop mysql-yum
		systemctl disable mysql-yum
		rm -rf /usr/lib/systemd/system/mysql-yum.service
		rm -rf /lib/systemd/system/mysql-yum.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ];then
# 	#初始化 
	cd ${rootPath} && python3 plugins/mysql-yum/index.py start ${type}
	cd ${rootPath} && python3 plugins/mysql-yum/index.py initd_install ${type}
fi
