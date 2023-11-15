#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

# for mac
export PATH=$PATH:/opt/homebrew/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
install_tmp=${rootPath}/tmp/mw_install.pl


action=$1
type=$2

echo $action $type

if id haproxy &> /dev/null ;then 
    echo "haproxy UID is `id -u haproxy`"
    echo "haproxy Shell is `grep "^haproxy:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd haproxy
	useradd -g haproxy haproxy
fi

if [ "${2}" == "" ];then
	echo '缺少安装脚本...'
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...'
	exit 0
fi

if [ "${action}" == "uninstall" ];then
	
	if [ -f /usr/lib/systemd/system/haproxy.service ] || [ -f /lib/systemd/system/haproxy.service ];then
		systemctl stop haproxy
		systemctl disable haproxy
		rm -rf /usr/lib/systemd/system/haproxy.service
		rm -rf /lib/systemd/system/haproxy.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d $serverPath/haproxy ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/haproxy/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/haproxy/index.py initd_install ${type}
fi
