#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

if id www &> /dev/null ;then 
    echo "www UID is `id -u www`"
    echo "www Shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	# useradd -g www -s /sbin/nologin www
	useradd -g www -s /bin/bash www
fi

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


if [ "${action}" == "uninstall" ] && [ -d ${serverPath}/php-apt/${type} ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py stop ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py initd_uninstall ${type}
fi

cd ${curPath} && sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d ${serverPath}/php-apt/${type} ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py initd_install ${type}
fi


