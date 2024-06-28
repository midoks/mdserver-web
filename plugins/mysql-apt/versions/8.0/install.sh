# -*- coding: utf-8 -*-
#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export DEBIAN_FRONTEND=noninteractive

# https://downloads.mysql.com/archives/community/

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl
myDir=${serverPath}/source/mysql-apt

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

# cd /www/server/mdserver-web/plugins/mysql-apt && bash install.sh install 8.0

# 暂时debian12没有标准版,先用11使用
# if [ "$OSNAME" == 'debian' ] && [ "$VERSION_ID" == '12' ] ;then 
# 	echo "暂时不支持该${OSNAME}${VERSION_ID}" > $install_tmp
# 	exit 1
# fi


ARCH="amd64"
TMP_ARCH=`arch`
if [ "$TMP_ARCH" == "x86_64" ];then
	ARCH="amd64"
elif [ "$TMP_ARCH" == "aarch64" ];then
	ARCH="arm64"
else
	ARCH="amd64"
fi

if [ "$ARCH" != "amd64" ];then
	echo "暂时不支持该${ARCH}" > $install_tmp
	exit 1
fi


MYSQL_VER=8.0.36
SUFFIX_NAME=${MYSQL_VER}-1${OSNAME}${VERSION_ID}_${ARCH}


# /lib/systemd/system/mysql.service
# /etc/mysql/my.cnf

APT_INSTALL()
{
########
mkdir -p $myDir
mkdir -p $serverPath/mysql-apt/bin


mkdir -p /var/run/mysqld
chown mysql -R /var/run/mysqld

wget  --no-check-certificate -O ${myDir}/mysql-server_${SUFFIX_NAME}.deb-bundle.tar https://cdn.mysql.com/archives/mysql-8.0/mysql-server_${SUFFIX_NAME}.deb-bundle.tar
chmod +x ${myDir}/mysql-server_${SUFFIX_NAME}.deb-bundle.tar
cd ${myDir} && tar vxf ${myDir}/mysql-server_${SUFFIX_NAME}.deb-bundle.tar

apt update -y
apt install -y libnuma1 libaio1 libmecab2

# 安装
dpkg -X mysql-common_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin



dpkg -X mysql-community-client-plugins_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin
dpkg -X mysql-community-client-core_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin
dpkg -X mysql-community-client_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin
dpkg -X mysql-client_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin

dpkg -X mysql-community-server-core_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin

dpkg -X mysql-community-server_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin
dpkg -X mysql-server_${SUFFIX_NAME}.deb $serverPath/mysql-apt/bin

# 测试时可关闭
rm -rf $myDir
#######
}

APT_UNINSTALL()
{
###
rm -rf $myDir
# apt remove -y mysql-server
###
}


Install_mysql()
{
	echo '正在安装脚本文件...' > $install_tmp

	isApt=`which apt`
	if [ "$isApt" != "" ];then
		APT_INSTALL
	fi

	if [ "$?" == "0" ];then
		mkdir -p $serverPath/mysql-apt
		echo '8.0' > $serverPath/mysql-apt/version.pl
		echo '安装完成' > $install_tmp
	else
		echo '8.0' > $serverPath/mysql-apt/version.pl
		echo "暂时不支持该系统" > $install_tmp
	fi
}

Uninstall_mysql()
{

	isApt=`which apt`
	if [ "$isApt" != "" ];then
		APT_UNINSTALL
	fi

	rm -rf $serverPath/mysql-apt
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_mysql
else
	Uninstall_mysql
fi
