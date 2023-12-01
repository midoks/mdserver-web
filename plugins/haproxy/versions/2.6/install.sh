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
	echo '正在安装Haproxy软件...'
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
			wget -O ${APP_DIR}/haproxy-${VERSION}.tar.gz https://dl.midoks.icu/soft/haproxy/haproxy-${VERSION}.tar.gz
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
	echo '安装Haproxy成功' > $install_tmp

	#Haproxy日志配置
	if [ -f /etc/rsyslog.conf ];then
		find_ha=`cat /etc/rsyslog.conf | grep haproxy`
		if [ "$find_ha" != "" ];then
			echo $find_ha
		else
			echo "---------------------------------------------"
			echo "" > ${serverPath}/haproxy/haproxy.log
			echo "local0.*  ${serverPath}/haproxy/haproxy.log" >> /etc/rsyslog.conf
			systemctl restart syslog
			echo "syslog默认的haproxy配置"
			echo "local0.*  ${serverPath}/haproxy/haproxy.log >> /etc/rsyslog.conf"
			echo "---------------------------------------------"
		fi
	fi

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
	echo "卸载Haproxy成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
