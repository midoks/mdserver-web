#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/manticoresearch && bash install.sh install latest
# cd /www/server/mdserver-web/plugins/manticoresearch && bash install.sh install code
# cd /www/server/mdserver-web/plugins/manticoresearch && bash install.sh install latest
# cd /www/server/mdserver-web && python3 plugins/manticoresearch/index.py run_status_test
# cd /www/server/mdserver-web && python3 plugins/manticoresearch/index.py start

# su -s /bin/sh manticore -c "indexer -c /etc/manticoresearch/manticore.conf xx --rotate"
# su -s /bin/sh manticore -c "indexer -c /etc/manticoresearch/manticore.conf xx_delta --rotate"

# systemctl status manticore
# systemctl restart manticore

if [ -f ${rootPath}/bin/activate ];then
	. ${rootPath}/bin/activate
fi

ACTION=$1
VERSION=$2

if [ "$sysName" == "Darwin" ];then
	sh -x $curPath/versions/mac/install.sh $1 $2
elif [ "$VERSION" == "code" ];then
	sh -x $curPath/versions/source/install.sh $1 $2
elif [ "$VERSION" == "debian" ];then
	sh -x $curPath/versions/apt/install.sh $1 $2
elif command -v apt >/dev/null 2>&1;then
	sh -x $curPath/versions/apt/install.sh $1 $2
elif command -v yum >/dev/null 2>&1;then
	sh -x $curPath/versions/yum/install.sh $1 $2
else
	echo "unsupported system: ${sysName}"
	exit 1
fi
