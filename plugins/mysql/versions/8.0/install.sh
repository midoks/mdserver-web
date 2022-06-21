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

Install_mysql()
{
	mkdir -p ${mysqlDir}
	echo '正在安装脚本文件...' > $install_tmp

	INSTALL_CMD=cmake
	if [ "$sysName" != "Darwin" ];then
		mkdir -p /var/log/mariadb
		touch /var/log/mariadb/mariadb.log
		groupadd mysql
		useradd -g mysql mysql

		INSTALL_CMD=cmake
	fi 

	if [ ! -f ${mysqlDir}/mysql-boost-8.0.25.tar.gz ];then
		wget -O ${mysqlDir}/mysql-boost-8.0.25.tar.gz https://cdn.mysql.com/archives/mysql-8.0/mysql-boost-8.0.25.tar.gz
	fi

	if [ ! -d ${mysqlDir}/mysql-8.0.25 ];then
		 cd ${mysqlDir} && tar -zxvf  ${mysqlDir}/mysql-boost-8.0.25.tar.gz
	fi

	if [ ! -d $serverPath/mysql ];then
		cd ${mysqlDir}/mysql-8.0.25 && ${INSTALL_CMD} \
		-DCMAKE_INSTALL_PREFIX=$serverPath/mysql \
		-DMYSQL_USER=mysql \
		-DMYSQL_TCP_PORT=3306 \
		-DMYSQL_UNIX_ADDR=/var/tmp/mysql.sock \
		-DWITH_MYISAM_STORAGE_ENGINE=1 \
		-DWITH_INNOBASE_STORAGE_ENGINE=1 \
		-DWITH_MEMORY_STORAGE_ENGINE=1 \
		-DENABLED_LOCAL_INFILE=1 \
		-DWITH_PARTITION_STORAGE_ENGINE=1 \
		-DEXTRA_CHARSETS=all \
		-DDEFAULT_CHARSET=utf8 \
		-DDEFAULT_COLLATION=utf8_general_ci \
		-DDOWNLOAD_BOOST=1 \
		-DFORCE_INSOURCE_BUILD=1 \
		-DWITH_BOOST=${mysqlDir}/mysql-8.0.25/boost/
		make && make install && make clean
		echo '8.0' > $serverPath/mysql/version.pl
		echo '安装完成' > $install_tmp
	fi
}

Uninstall_mysql()
{
	rm -rf $serverPath/mysql
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_mysql
else
	Uninstall_mysql
fi
