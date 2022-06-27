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
sysName=`uname`


install_tmp=${rootPath}/tmp/mw_install.pl
mysqlDir=${serverPath}/source/mysql


# 加快测试速度 For Github Action
MAKEJN="${SYS_MAKEJN:-'-j2'}"
echo "SYS_MAKEJN:$MAKEJN"

Install_mysql()
{
	mkdir -p ${mysqlDir}
	echo '正在安装脚本文件...' > $install_tmp

	if id mysql &> /dev/null ;then 
	    echo "mysql UID is `id -u www`"
	    echo "mysql Shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
	else
	    groupadd mysql
		useradd -g mysql mysql
	fi

	if [ "$sysName" != "Darwin" ];then
		mkdir -p /var/log/mariadb
		touch /var/log/mariadb/mariadb.log
	fi 
	

	if [ ! -f ${mysqlDir}/mysql-5.6.50.tar.gz ];then
		wget -O ${mysqlDir}/mysql-5.6.50.tar.gz https://cdn.mysql.com/Downloads/MySQL-5.6/mysql-5.6.50.tar.gz
	fi

	if [ ! -d ${mysqlDir}/mysql-5.6.50 ];then
		 cd ${mysqlDir} && tar -zxvf  ${mysqlDir}/mysql-5.6.50.tar.gz
	fi
	

	if [ ! -d $serverPath/mysql ];then
		cd ${mysqlDir}/mysql-5.6.50 && cmake \
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
		-DDEFAULT_CHARSET=utf8mb4 \
		-DCMAKE_C_COMPILER=/usr/bin/gcc \
		-DCMAKE_CXX_COMPILER=/usr/bin/g++ \
		-DDEFAULT_COLLATION=utf8mb4_general_ci \
		&& make $MAKEJN && make install && make clean


		if [ -d $serverPath/mysql ];then
			echo '5.6' > $serverPath/mysql/version.pl
			echo '安装完成' > $install_tmp
		else
			echo '安装失败' > $install_tmp
		fi
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
