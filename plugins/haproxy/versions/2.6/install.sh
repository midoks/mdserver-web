#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl


bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


VERSION=2.6.4
MIN_VERSION=2.6
Install_App()
{

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/haproxy

	APP_DIR=${serverPath}/source/haproxy
	mkdir -p $APP_DIR


	LOCAL_ADDR=common
    cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
    if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
        LOCAL_ADDR=cn
    fi


    if [ "${LOCAL_ADDR}" == "cn" ];then
    	if [ ! -f ${APP_DIR}/haproxy-${VERSION}.tar.gz ];then
			wget -O ${APP_DIR}/haproxy-${VERSION}.tar.gz https://dl.midoks.me/soft/haproxy/haproxy-${VERSION}.tar.gz
		fi
    fi

	
	if [ ! -f ${APP_DIR}/haproxy-${VERSION}.tar.gz ];then
		if [ $sysName == 'Darwin' ]; then
			wget --no-check-certificate -O ${APP_DIR}/haproxy-${VERSION}.tar.gz https://www.haproxy.org/download/${MIN_VERSION}/src/haproxy-${VERSION}.tar.gz
		else
			curl -sSLo ${APP_DIR}/haproxy-${VERSION}.tar.gz https://www.haproxy.org/download/${MIN_VERSION}/src/haproxy-${VERSION}.tar.gz
		fi
	fi

	if [ ! -f ${APP_DIR}/haproxy-${VERSION}.tar.gz ];then
		curl -sSLo ${APP_DIR}/haproxy-${VERSION}.tar.gz https://www.haproxy.org/download/${MIN_VERSION}/src/haproxy-${VERSION}.tar.gz
	fi


	cd ${APP_DIR} && tar -zxvf haproxy-${VERSION}.tar.gz

	if [ "$OSNAME" == "macos" ];then
		cd ${APP_DIR}/haproxy-${VERSION} && make TARGET=osx && make install PREFIX=$serverPath/haproxy
	else
		cd ${APP_DIR}/haproxy-${VERSION} && make TARGET=linux-glibc && make install PREFIX=$serverPath/haproxy
	fi

	echo $MIN_VERSION > $serverPath/haproxy/version.pl
	echo 'Install_HA' > $install_tmp

	#删除解压源码
	if [ -d ${APP_DIR}/haproxy-${VERSION} ];then
		rm -rf ${APP_DIR}/haproxy-${VERSION}
	fi
}

Uninstall_App()
{
	if [ -f $serverPath/haproxy/initd/haproxy ];then
		$serverPath/haproxy/initd/haproxy stop
	fi

	rm -rf $serverPath/haproxy
	echo "Uninstall_HA" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
