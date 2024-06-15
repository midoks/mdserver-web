#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# https://downloads.mysql.com/archives/community/

# cd /www/server/mdserver-web/plugins/mysql-apt && bash install.sh install 8.0
# cd /www/server/mdserver-web/plugins/mysql-apt && bash install.sh uninstall 8.0
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql-apt/index.py start 5.7
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mysql-apt/index.py fix_db_access
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/mysql/index.py do_full_sync  {"db":"xxx","sign":"","begin":1}

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
	
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-apt/index.py stop ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-apt/index.py initd_uninstall ${type}
	cd $curPath

	if [ -f /usr/lib/systemd/system/mysql-apt.service ] || [ -f /lib/systemd/system/mysql-apt.service ];then
		systemctl stop mysql-apt
		systemctl disable mysql-apt
		rm -rf /usr/lib/systemd/system/mysql-apt.service
		rm -rf /lib/systemd/system/mysql-apt.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ];then
	#初始化

	if [ "$?" != "0" ];then
		exit $?
	fi
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-apt/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-apt/index.py initd_install ${type}
fi
