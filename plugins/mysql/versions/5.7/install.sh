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

VERSION=5.7.39


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

	# ----- cpu start ------
	if [ -z "${cpuCore}" ]; then
    	cpuCore="1"
	fi

	if [ -f /proc/cpuinfo ];then
		cpuCore=`cat /proc/cpuinfo | grep "processor" | wc -l`
	fi

	MEM_INFO=$(free -m|grep Mem|awk '{printf("%.f",($2)/1024)}')
	if [ "${cpuCore}" != "1" ] && [ "${MEM_INFO}" != "0" ];then
	    if [ "${cpuCore}" -gt "${MEM_INFO}" ];then
	        cpuCore="${MEM_INFO}"
	    fi
	else
	    cpuCore="1"
	fi

	if [ "$cpuCore" -gt "1" ];then
		cpuCore=`echo "$cpuCore" | awk '{printf("%.f",($1)*0.8)}'`
	fi
	# ----- cpu end ------

	cd ${rootPath}/plugins/mysql/lib && /bin/bash rpcgen.sh

	if [ ! -f ${mysqlDir}/mysql-boost-${VERSION}.tar.gz ];then
		wget -O ${mysqlDir}/mysql-boost-${VERSION}.tar.gz --tries=3 https://cdn.mysql.com/archives/mysql-5.7/mysql-boost-${VERSION}.tar.gz
	fi

	#检测文件是否损坏.
	md5_mysql_ok=d949b0ef81c3f52f7ef0874066244221
	if [ -f ${mysqlDir}/mysql-boost-${VERSION}.tar.gz ];then
		md5_mysql=`md5sum ${mysqlDir}/mysql-boost-${VERSION}.tar.gz  | awk '{print $1}'`
		if [ "${md5_mysql_ok}" == "${md5_mysql}" ]; then
			echo "mysql5.7 file check ok"
		else
			# 重新下载
			rm -rf ${mysqlDir}/mysql-${VERSION}
			wget -O ${mysqlDir}/mysql-boost-${VERSION}.tar.gz --tries=3 https://cdn.mysql.com/archives/mysql-5.7/mysql-boost-${VERSION}.tar.gz
		fi
	fi

	if [ ! -d ${mysqlDir}/mysql-${VERSION} ];then
		 cd ${mysqlDir} && tar -zxvf  ${mysqlDir}/mysql-boost-${VERSION}.tar.gz
	fi

	OPTIONS=''
	##check openssl version
	OPENSSL_VERSION=`openssl version|awk '{print $2}'|awk -F '.' '{print $1}'`
	if [ "${OPENSSL_VERSION}" -ge "3" ];then
		#openssl version to high
		cd ${rootPath}/plugins/php/lib && /bin/bash openssl.sh
		export PKG_CONFIG_PATH=$serverPath/lib/openssl/lib/pkgconfig
		OPTIONS="-DWITH_SSL=${serverPath}/lib/openssl"
	fi

	if [ ! -d $serverPath/mysql ];then
		cd ${mysqlDir}/mysql-${VERSION} && cmake \
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
		$OPTIONS \
		-DCMAKE_C_COMPILER=/usr/bin/gcc \
		-DCMAKE_CXX_COMPILER=/usr/bin/g++ \
		-DWITH_BOOST=${mysqlDir}/mysql-${VERSION}/boost/
		make -j${cpuCore} && make install && make clean

		if [ -d $serverPath/mysql ];then
			echo '5.7' > $serverPath/mysql/version.pl
			echo '安装完成' > $install_tmp
		else
			# rm -rf ${mysqlDir}/mysql-${VERSION}
			echo '安装失败' > $install_tmp
			echo 'install fail'>&2
			exit 1
		fi
	fi
}

Uninstall_mysql()
{
	rm -rf $serverPath/mysql
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == "install" ];then
	Install_mysql
else
	Uninstall_mysql
fi
