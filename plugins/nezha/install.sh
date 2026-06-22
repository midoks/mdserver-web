#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# systemctl start nezha-dashboard
# systemctl status nezha-dashboard

# cd /www/server/mdserver-web/plugins/nezha && bash install.sh install 2.2.6
# sqlite3 /www/server/nezha/dashboard/data/sqlite.db "DELETE FROM users;"

# cd /www/server/mdserver-web && source bin/activate && python3 plugins/nezha/index.py start
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/nezha/index.py status

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

action=$1
type=$2

if [ "${2}" == "" ];then
	echo '缺少安装脚本...'
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...'
	exit 0
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "uninstall" ];then
	if [ -f /usr/lib/systemd/system/nezha.service ] || [ -f /lib/systemd/system/nezha.service ] ;then
		systemctl stop nezha
		systemctl disable nezha
		rm -rf /usr/lib/systemd/system/nezha.service
		rm -rf /lib/systemd/system/nezha.service
		systemctl daemon-reload
	fi
fi
