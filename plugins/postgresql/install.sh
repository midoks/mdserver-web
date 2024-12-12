#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/postgresql && bash install.sh install 16

action=$1
type=$2

VERSION=(${type//./ })

pip install psycopg2-binary
if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
	pip install psycopg2-binary
fi


if [ "${2}" == "" ];then
	echo '缺少安装脚本...'
	exit 0
fi 

if [ ! -d $curPath/versions/$VERSION ];then
	echo '缺少安装脚本2...'
	exit 0
fi

if [ "${action}" == "uninstall" ];then
	if [ -f /usr/lib/systemd/system/postgresql.service ] || [ -f /lib/systemd/system/postgresql.service ];then
		systemctl stop postgresql
		systemctl disable postgresql
		rm -rf /usr/lib/systemd/system/postgresql.service
		rm -rf /lib/systemd/system/postgresql.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$VERSION/install.sh $1

if [ "${action}" == "install" ] && [ -d $serverPath/postgresql ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/postgresql/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/postgresql/index.py initd_install ${type}
fi
