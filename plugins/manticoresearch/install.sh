#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
export LANG=en_US.UTF-8
export DEBIAN_FRONTEND=noninteractive

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/manticoresearch && bash install.sh install latest
# cd /www/server/mdserver-web/plugins/manticoresearch && bash install.sh install code
# cd /www/server/mdserver-web/plugins/manticoresearch && bash install.sh install latest
# cd /www/server/mdserver-web/plugins/manticoresearch && bash install.sh install 29.9
# cd /www/server/mdserver-web && python3 plugins/manticoresearch/index.py run_status_test
# cd /www/server/mdserver-web && python3 plugins/manticoresearch/index.py start
# cd /www/server/mdserver-web && python3 plugins/manticoresearch/index.py rebuild

# su -s /bin/sh manticore -c "indexer -c /etc/manticoresearch/manticore.conf xx --rotate"
# su -s /bin/sh manticore -c "indexer -c /etc/manticoresearch/manticore.conf xx_delta --rotate"

# systemctl status manticore
# systemctl restart manticore

if [ -f ${rootPath}/bin/activate ];then
	. ${rootPath}/bin/activate
fi

ACTION=$1
VERSION=$2

# 版本优先
if [ -f $curPath/versions/${VERSION}/install.sh ];then
	sh -x $curPath/versions/${VERSION}/install.sh ${ACTION} ${VERSION}
	exit 0
fi

if [ "$sysName" == "Darwin" ];then
	sh -x $curPath/versions/mac/install.sh ${ACTION} ${VERSION}
elif [ "$VERSION" == "code" ];then
	sh -x $curPath/versions/source/install.sh ${ACTION} ${VERSION}
elif [ "$VERSION" == "debian" ];then
	sh -x $curPath/versions/apt/install.sh ${ACTION} ${VERSION}
elif command -v apt >/dev/null 2>&1;then
	sh -x $curPath/versions/apt/install.sh ${ACTION} ${VERSION}
elif command -v yum >/dev/null 2>&1;then
	sh -x $curPath/versions/yum/install.sh ${ACTION} ${VERSION}
else
	echo "unsupported system: ${sysName}"
	exit 1
fi
