# -*- coding: utf-8 -*-
#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

#https://dev.mysql.com/downloads/mysql/5.6.html
#https://dev.mysql.com/downloads/file/?id=489600

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/mw_install.pl
mysqlDir=${serverPath}/source/mysql

Install_mysql()
{
	mkdir -p ${mysqlDir}
	echo '正在安装脚本文件...' > $install_tmp

	mkdir -p /var/log/mariadb
	touch /var/log/mariadb/mariadb.log

	groupadd mysql
	useradd -g mysql mysql

	if [ ! -f ${mysqlDir}/mysql-5.6.46.tar.gz ];then
		wget -O ${mysqlDir}/mysql-5.6.46.tar.gz https://cdn.mysql.com//Downloads/MySQL-5.6/mysql-5.6.46.tar.gz
	fi

	if [ ! -d ${mysqlDir}/mysql-5.6.46 ];then
		 cd ${mysqlDir} && tar -zxvf  ${mysqlDir}/mysql-5.6.46.tar.gz
	fi
	

	cd ${mysqlDir}/mysql-5.6.46 && cmake \
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
	&& make && make install && make clean
	echo '5.6' > $serverPath/mysql/version.pl
	echo '安装完成' > $install_tmp
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
