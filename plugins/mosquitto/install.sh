#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
echo "use system: ${sysName}"

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/mosquitto && bash install.sh install 2.0.18
# cd /www/mdserver-web/plugins/mosquitto && bash install.sh install 2.0.18

install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=$2

Install_App()
{
	if id mosquitto &> /dev/null ;then 
	    echo "mosquitto UID is `id -u mosquitto`"
	    echo "mosquitto Shell is `grep "^mosquitto:" /etc/passwd |cut -d':' -f7 `"
	else
	    groupadd mosquitto
		useradd -g mosquitto mosquitto
	fi

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	if [ ! -f $serverPath/source/mosquitto-${VERSION}.tar.gz ];then
		wget --no-check-certificate -O $serverPath/source/mosquitto-${VERSION}.tar.gz https://mosquitto.org/files/source/mosquitto-${VERSION}.tar.gz
	fi
	
	if [ ! -d mosquitto-${VERSION} ];then
		cd $serverPath/source && tar -zxvf mosquitto-${VERSION}.tar.gz
	fi


	INSTALL_CMD=cmake
	# check cmake version
	CMAKE_VERSION=`cmake -version | grep version | awk '{print $3}' | awk -F '.' '{print $1}'`
	if [ "$CMAKE_VERSION" -eq "2" ];then
		mkdir -p /var/log/mariadb
		touch /var/log/mariadb/mariadb.log
		INSTALL_CMD=cmake3
	fi

	mkdir -p $serverPath/mosquitto
	if  [ ! -d $serverPath/mosquitto/bin ];then
		cd mosquitto-${VERSION} && ${INSTALL_CMD} CMakeLists.txt -DCMAKE_INSTALL_PREFIX=$serverPath/mosquitto && make install
	fi
	
	if [ -d $serverPath/mosquitto ];then
		echo "${VERSION}" > $serverPath/mosquitto/version.pl
		echo '安装完成' > $install_tmp


		cd ${rootPath} && python3 ${rootPath}/plugins/mosquitto/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/mosquitto/index.py initd_install
	fi
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/mosquitto.service ];then
		systemctl stop mosquitto
		systemctl disable mosquitto
		rm -rf /usr/lib/systemd/system/mosquitto.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/mosquitto/initd/mosquitto ];then
		$serverPath/mosquitto/initd/mosquitto stop
	fi

	rm -rf $serverPath/mosquitto
	echo "uninstall mosquitto" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
