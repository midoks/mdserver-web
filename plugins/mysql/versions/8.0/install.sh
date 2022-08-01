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

_os=`uname`
echo "use system: ${_os}"
if [ ${_os} == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eq "openSUSE" /etc/*-release; then
	OSNAME='opensuse'
	zypper refresh
elif grep -Eq "FreeBSD" /etc/*-release; then
	OSNAME='freebsd'
	pkg install -y wget unzip
elif grep -Eqi "Arch" /etc/issue || grep -Eq "Arch" /etc/*-release; then
	OSNAME='arch'
	echo y | pacman -Sy unzip
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
	yum install -y wget zip unzip
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
	yum install -y wget zip unzip
elif grep -Eqi "Rocky" /etc/issue || grep -Eq "Rocky" /etc/*-release; then
	OSNAME='rocky'
	yum install -y wget zip unzip
elif grep -Eqi "AlmaLinux" /etc/issue || grep -Eq "AlmaLinux" /etc/*-release; then
	OSNAME='alma'
	yum install -y wget zip unzip
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
	apt update -y
	apt install -y devscripts
	apt install -y wget zip unzip
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
	apt install -y wget zip unzip
else
	OSNAME='unknow'
fi

VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`



VERSION=8.0.29


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

	if [ -z "${cpuCore}" ]; then
    	cpuCore="1"
	fi

	MEM_INFO=$(free -m|grep Mem|awk '{printf("%.f",($2)/1024)}')
	if [ "${cpuCore}" != "1" ] && [ "${MEM_INFO}" != "0" ];then
	    if [ "${cpuCore}" -gt "${MEM_INFO}" ];then
	        cpuCore="${MEM_INFO}"
	    fi
	else
	    cpuCore="1"
	fi

	cd $serverPath/mdserver-web/plugins/mysql/lib && /bin/bash rpcgen.sh

	INSTALL_CMD=cmake
	# check cmake version
	CMAKE_VERSION=`cmake -version | grep version | awk '{print $3}' | awk -F '.' '{print $1}'`
	if [ "$CMAKE_VERSION" -eq "2" ];then
		mkdir -p /var/log/mariadb
		touch /var/log/mariadb/mariadb.log
		INSTALL_CMD=cmake3
	fi

	if [ ! -f ${mysqlDir}/mysql-boost-${VERSION}.tar.gz ];then
		wget -O ${mysqlDir}/mysql-boost-${VERSION}.tar.gz --tries=3 https://cdn.mysql.com/Downloads/MySQL-8.0/mysql-boost-${VERSION}.tar.gz
	fi

	#检测文件是否损坏.
	md5_mysql_ok=42fbfe0569089c20f9aa457b3f367d50
	if [ -f ${mysqlDir}/mysql-boost-${VERSION}.tar.gz ];then
		md5_mysql=`md5sum ${mysqlDir}/mysql-boost-${VERSION}.tar.gz  | awk '{print $1}'`
		if [ "${md5_mysql_ok}" == "${md5_mysql}" ]; then
			echo "mysql8.0 file  check ok"
		else
			# 重新下载
			rm -rf ${mysqlDir}/mysql-${VERSION}
			wget -O ${mysqlDir}/mysql-boost-${VERSION}.tar.gz --tries=3 https://cdn.mysql.com/Downloads/MySQL-8.0/mysql-boost-${VERSION}.tar.gz
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
		cd $serverPath/mdserver-web/plugins/php/lib && /bin/bash openssl.sh
		export PKG_CONFIG_PATH=$serverPath/lib/openssl/lib/pkgconfig
		OPTIONS="-DWITH_SSL=${serverPath}/lib/openssl"
	fi

	WHERE_DIR_GCC=/usr/bin/gcc
	WHERE_DIR_GPP=/usr/bin/g++
	if [ "$OSNAME" == "centos" ] && [ "$VERSION_ID" == "7" ];then
		# yum install centos-release-scl -y
		# yum install devtoolset-7 -y
		# scl enable devtoolset-7 bash
		yum install centos-release-scl-rh -y
        yum install devtoolset-7-gcc devtoolset-7-gcc-c++ -y
        # yum install cmake3 -y

		gcc --version
		WHERE_DIR_GCC=/opt/rh/devtoolset-7/root/usr/bin/gcc
		WHERE_DIR_GPP=/opt/rh/devtoolset-7/root/usr/bin/g++
		echo $WHERE_DIR_GCC
		echo $WHERE_DIR_GPP
	fi

	if [ ! -d $serverPath/mysql ];then
		cd ${mysqlDir}/mysql-${VERSION} && ${INSTALL_CMD} \
		-DCMAKE_INSTALL_PREFIX=$serverPath/mysql \
		-DMYSQL_USER=mysql \
		-DMYSQL_TCP_PORT=3306 \
		-DMYSQL_UNIX_ADDR=/var/tmp/mysql.sock \
		-DWITH_MYISAM_STORAGE_ENGINE=1 \
		-DWITH_INNOBASE_STORAGE_ENGINE=1 \
		-DWITH_MEMORY_STORAGE_ENGINE=1 \
		-DENABLED_LOCAL_INFILE=1 \
		-DWITH_PARTITION_STORAGE_ENGINE=1 \
		-DWITH_READLINE=1 \
		-DEXTRA_CHARSETS=all \
		-DDEFAULT_CHARSET=utf8mb4 \
		-DDEFAULT_COLLATION=utf8mb4_general_ci \
		-DDOWNLOAD_BOOST=1 \
		-DFORCE_INSOURCE_BUILD=1 \
		$OPTIONS \
		-DCMAKE_C_COMPILER=$WHERE_DIR_GCC \
		-DCMAKE_CXX_COMPILER=$WHERE_DIR_GPP \
		-DWITH_BOOST=${mysqlDir}/mysql-${VERSION}/boost/
		make -j${cpuCore} && make install && make clean

		if [ -d $serverPath/mysql ];then
			echo '8.0' > $serverPath/mysql/version.pl
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
