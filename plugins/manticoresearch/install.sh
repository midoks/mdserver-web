#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`

# cd /www/server/mdserver-web/plugins/manticoresearch && bash install.sh install 7.4.6
# cd /www/server/mdserver-web && python3 plugins/manticoresearch/index.py run_status_test
# cd /www/server/mdserver-web && python3 plugins/manticoresearch/index.py start
# systemctl status manticore
# systemctl restart manticore

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

ACTION=$1
VERSION=$2

which apt
if [ "$?" == "0" ];then
	sh -x $curPath/versions/apt/install.sh $1 $2
fi

which yum
if [ "$?" == "0" ];then
	sh -x $curPath/versions/yum/install.sh $1 $2
fi
