#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/maridb && bash install.sh install 8.2
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/maridb/index.py try_slave_sync_bugfix {}
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/maridb/index.py do_full_sync  {"db":"xxx","sign":"","begin":1}
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/maridb/index.py sync_database_repair  {"db":"xxx","sign":""}
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/maridb/index.py init_slave_status
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/maridb/index.py install_pre_inspection

install_tmp=${rootPath}/tmp/mw_install.pl


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
	
	if [ -f /usr/lib/systemd/system/mariadb.service ] || [ -f /lib/systemd/system/mariadb.service ];then
		systemctl stop mariadb
		systemctl disable mariadb
		rm -rf /usr/lib/systemd/system/mariadb.service
		rm -rf /lib/systemd/system/mariadb.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d $serverPath/mariadb ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/mariadb/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/mariadb/index.py initd_install ${type}
fi
