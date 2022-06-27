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

# 加快测试速度 For Github Action
MAKEJN='${SYS_MAKEJN:+"-j2"}'
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

	INSTALL_CMD=cmake
	if [ "$sysName" != "Darwin" ];then
		mkdir -p /var/log/mariadb
		touch /var/log/mariadb/mariadb.log
		INSTALL_CMD=cmake
	fi 

	if [ ! -f ${mysqlDir}/mysql-boost-8.0.25.tar.gz ];then
		wget -O ${mysqlDir}/mysql-boost-8.0.25.tar.gz https://cdn.mysql.com/archives/mysql-8.0/mysql-boost-8.0.25.tar.gz
	fi

	#检测文件是否损坏.
	md5_mysql_ok=e142c2058313b4646c36fa9bb1b38493
	if [ -f ${mysqlDir}/mysql-boost-8.0.25.tar.gz ];then
		md5_mysql=`md5sum ${mysqlDir}/mysql-boost-8.0.25.tar.gz  | awk '{print $1}'`
		if [ "${md5_mysql_ok}" == "${md5_mysql}" ]; then
			echo "mysql8.0 file  check ok"
		else
			# 重新下载
			rm -rf ${mysqlDir}/mysql-8.0.25
			wget -O ${mysqlDir}/mysql-boost-8.0.25.tar.gz https://cdn.mysql.com/archives/mysql-8.0/mysql-boost-8.0.25.tar.gz
		fi
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
		-DDEFAULT_CHARSET=utf8mb4 \
		-DDEFAULT_COLLATION=utf8mb4_general_ci \
		-DDOWNLOAD_BOOST=1 \
		-DFORCE_INSOURCE_BUILD=1 \
		-DCMAKE_C_COMPILER=/usr/bin/gcc \
		-DCMAKE_CXX_COMPILER=/usr/bin/g++ \
		-DWITH_BOOST=${mysqlDir}/mysql-8.0.25/boost/
		make $MAKEJN && make install && make clean

		if [ -d $serverPath/mysql ];then
			echo '8.0' > $serverPath/mysql/version.pl
		fi
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
