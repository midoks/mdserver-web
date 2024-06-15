#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# 手动主从设置
# https://www.cnblogs.com/whiteY/p/17331882.html

# cd /www/server/mdserver-web/plugins/mysql && bash install.sh install 8.2
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/mysql/index.py try_slave_sync_bugfix {}
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/mysql/index.py do_full_sync  {"db":"xxx","sign":"","begin":1}
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/mysql/index.py sync_database_repair  {"db":"xxx","sign":""}
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/mysql/index.py init_slave_status
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/mysql/index.py install_pre_inspection
curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


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

if [ -d $serverPath/mysql ];then
	exit 0
fi

if [ "${action}" == "uninstall" ];then
	
	if [ -f /usr/lib/systemd/system/mysql.service ] || [ -f /lib/systemd/system/mysql.service ];then
		systemctl stop mysql
		systemctl disable mysql
		rm -rf /usr/lib/systemd/system/mysql.service
		rm -rf /lib/systemd/system/mysql.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d $serverPath/mysql ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql/index.py initd_install ${type}
fi
