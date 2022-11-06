# -*- coding: utf-8 -*-
#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

#https://dev.mysql.com/downloads/mysql/5.7.html
#https://dev.mysql.com/downloads/file/?id=489855

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl
mysqlDir=${serverPath}/source/mysql

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

# cd /www/server/mdserver-web/plugins/mysql-apt && bash install.sh install 8.0

MYSQL_VER=8.0.31
SUFFIX_NAME=${MYSQL_VER}-1${OSNAME}${VERSION_ID}_amd64


# /lib/systemd/system/mysql.service
# /etc/mysql/my.cnf

APT_INSTALL()
{
########
wget -O /tmp/mysql-server_${SUFFIX_NAME}.deb-bundle.tar https://cdn.mysql.com//Downloads/MySQL-8.0/mysql-server_${SUFFIX_NAME}.deb-bundle.tar
chmod +x /tmp/mysql-server_${SUFFIX_NAME}.deb-bundle.tar
tar vxf /tmp/mysql-server_${SUFFIX_NAME}.deb-bundle.tar

apt update -y
apt install -y libnuma1 libaio1 libmecab2

# 手动调试
# dpkg -i mysql-common_8.0.31-1ubuntu18.04_amd64.deb
# dpkg -i mysql-community-client-plugins_8.0.31-1ubuntu18.04_amd64.deb
# dpkg -i mysql-community-client-core_8.0.31-1ubuntu18.04_amd64.deb
# dpkg -i mysql-community-client_8.0.29-1ubuntu18.04_amd64.deb
# dpkg -i mysql-client_8.0.31-1ubuntu18.04_amd64.deb


dpkg -i mysql-common_${SUFFIX_NAME}.deb

# dpkg-preconfigure mysql-community-server_8.0.29-1ubuntu18.04_amd64.deb
export DEBIAN_FRONTEND=noninteractive
dpkg -i mysql-community-client-plugins_${SUFFIX_NAME}.deb
dpkg -i mysql-community-client-core_${SUFFIX_NAME}.deb
dpkg -i mysql-community-client_${SUFFIX_NAME}.deb
dpkg -i mysql-client_${SUFFIX_NAME}.deb

# dpkg -i mysql-community-client-plugins_${SUFFIX_NAME}.deb
# dpkg -i mysql-community-client_${SUFFIX_NAME}.deb

# dpkg -i mysql-client_${SUFFIX_NAME}.deb
# dpkg -i libmysqlclient-dev_${SUFFIX_NAME}.deb
# dpkg -i libmysqld-dev_${SUFFIX_NAME}.deb
# dpkg -i mysql-community-${SUFFIX_NAME}.deb
# dpkg -i mysql-client_${SUFFIX_NAME}.deb
# dpkg -i mysql-common_${SUFFIX_NAME}.deb

# apt -f install
# apt -f install libmecab2

dpkg -i mysql-community-server-core_${SUFFIX_NAME}.deb
dpkg -i mysql-community-server_${SUFFIX_NAME}.deb
dpkg -i mysql-server_${SUFFIX_NAME}.deb

# dpkg -i mysql-server_${SUFFIX_NAME}.deb
# apt -f install
# apt install -y mysql-server
# rm -rf /tmp/mysql-server_8.0.29-1debian11_amd64.deb-bundle.tar
#######
}

APT_UNINSTALL()
{
###
apt remove -y mysql-server
###
}


Install_mysql()
{

	echo '正在安装脚本文件...' > $install_tmp

	if id mysql &> /dev/null ;then 
	    echo "mysql UID is `id -u mysql`"
	    echo "mysql Shell is `grep "^mysql:" /etc/passwd |cut -d':' -f7 `"
	else
	    groupadd mysql
		useradd -g mysql mysql
	fi


	isApt=`which apt`
	if [ "$isApt" != "" ];then
		APT_INSTALL
	fi

	if [ "$?" == "0" ];then
		mkdir -p $serverPath/mysql-apt
		echo '8.0' > $serverPath/mysql-apt/version.pl
		echo '安装完成' > $install_tmp
	else
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
