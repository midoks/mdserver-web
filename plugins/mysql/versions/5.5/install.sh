#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

#https://dev.mysql.com/downloads/mysql/5.5.html#downloads
#https://dev.mysql.com/downloads/file/?id=480541

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`

mysqlDir=${serverPath}/source/mysql

VERSION=5.5.62

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


Install_common(){
	apt install -y libudev-dev
	apt install -y libtirpc-dev
	apt install -y libssl-dev
	apt install -y libgssglue-dev
	apt install -y software-properties-common

	apt install -y build-essential
	apt install -y cmake 
	apt install -y pkg-config 
	apt install -y libncurses5-dev
	apt install -y libsystemd-dev 
	apt install -y libsasl2-dev 
	apt install -y libldap2-dev 
}

# 安装依赖
Install_dep(){
	Install_common
	add-apt-repository -y ppa:ubuntu-toolchain-r/test

	export PKG_CONFIG_PATH=/usr/lib/pkgconfig
	apt install -y gcc-10 g++-10
	WHERE_DIR_GCC=/usr/bin/gcc-10
	WHERE_DIR_GPP=/usr/bin/g++-10
}

Install_dep_debain13(){
	Install_common
	# add-apt-repository -y ppa:ubuntu-toolchain-r/test
	export PKG_CONFIG_PATH=/usr/lib/pkgconfig
	apt install -y gcc-12 g++-12
	WHERE_DIR_GCC=/usr/bin/gcc-12
	WHERE_DIR_GPP=/usr/bin/g++-12
}

Install_mysql()
{
	mkdir -p ${mysqlDir}
	echo '正在安装脚本文件...'

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

	if [ "$cpuCore" -gt "2" ];then
		cpuCore=`echo "$cpuCore" | awk '{printf("%.f",($1)*0.8)}'`
	else
		cpuCore="1"
	fi
	# ----- cpu end ------

	if [ ! -f ${mysqlDir}/mysql-${VERSION}.tar.gz ];then
		wget --no-check-certificate -O ${mysqlDir}/mysql-${VERSION}.tar.gz --tries=3 https://dev.mysql.com/get/Downloads/MySQL-5.5/mysql-${VERSION}.tar.gz
	fi

	if [ ! -d ${mysqlDir}/mysql-${VERSION} ];then
		 cd ${mysqlDir} && tar -zxvf  ${mysqlDir}/mysql-${VERSION}.tar.gz
	fi
	
	WHERE_DIR_GCC=/usr/bin/gcc
	WHERE_DIR_GPP=/usr/bin/g++
	if [ ! -f $WHERE_DIR_GCC ];then
		WHERE_DIR_GCC=`which gcc`
	fi

	if [ ! -f $WHERE_DIR_GPP ];then
		WHERE_DIR_GPP=`which g++`
	fi

	# https://blog.whsir.com/post-7748.html
	# arm架构编译MySQL5.5报错
	if [[ "$sysArch" =~  "aarch" ]];then
		# wget --no-check-certificate -O ${mysqlDir}/mysql-5.5-fix-arm-client_plugin.patch https://down.whsir.com/downloads/mysql-5.5-fix-arm-client_plugin.patch
		cd ${mysqlDir}/mysql-5.5.62 && patch -p1 < ${rootPath}/plugins/mysql/patch/mysql-5.5-fix-arm-client_plugin.patch
	fi

	if [ "$OSNAME" == "ubuntu" ];then
		Install_dep
	fi

	OPTIONS=''

	if [ "$OSNAME" == "debian" ] && [ "$VERSION_ID" == "13" ];then
		Install_dep_debain13
		# export CFLAGS="-D__s64=long long -D__u64='unsigned long long' -D__s32=int -D__u32='unsigned int' -D__u16='unsigned short'"
		# export CXXFLAGS="$CFLAGS"
		# OPTIONS="${OPTIONS} -DCMAKE_C_FLAGS=${CFLAGS}"
		# OPTIONS="${OPTIONS} -DCMAKE_CXX_FLAGS=${CXXFLAGS}"

		cd ${rootPath}/plugins/php/lib && /bin/bash openssl_10.sh
		export PKG_CONFIG_PATH=${serverPath}/lib/openssl10/lib/pkgconfig
		OPTIONS="-DWITH_SSL=${serverPath}/lib/openssl10"

		# 经过测试，无法安装
		echo "debain13不支持5.5低版本编译"
		exit 0
	fi

	if [ ! -d $serverPath/mysql ];then
		cd ${mysqlDir}/mysql-5.5.62 && cmake \
		-DCMAKE_INSTALL_PREFIX=$serverPath/mysql \
		-DMYSQL_USER=mysql \
		-DMYSQL_TCP_PORT=3306 \
		-DMYSQL_UNIX_ADDR=/var/tmp/mysql.sock \
		-DWITH_MYISAM_STORAGE_ENGINE=1 \
		-DWITH_INNOBASE_STORAGE_ENGINE=1 \
		-DWITH_MEMORY_STORAGE_ENGINE=1 \
		-DENABLED_LOCAL_INFILE=1 \
		-DWITH_PARTITION_STORAGE_ENGINE=1 \
		$OPTIONS \
		-DEXTRA_CHARSETS=all \
		-DDEFAULT_CHARSET=utf8mb4 \
		-DDEFAULT_COLLATION=utf8mb4_general_ci \
		-DCMAKE_C_COMPILER=$WHERE_DIR_GCC \
		-DCMAKE_CXX_COMPILER=$WHERE_DIR_GPP
		make -j${cpuCore} && make install && make clean

		if [ -d $serverPath/mysql ];then
			rm -rf ${mysqlDir}/mysql-${VERSION}
			echo '5.5' > $serverPath/mysql/version.pl
			echo "${VERSION}安装完成"
		else
			# rm -rf ${mysqlDir}/mysql-5.5.62
			echo "${VERSION}安装失败"
			exit 1
		fi
	fi
}

Uninstall_mysql()
{
	rm -rf $serverPath/mysql
	echo '卸载完成'
}

action=$1
if [ "${1}" == "install" ];then
	Install_mysql
else
	Uninstall_mysql
fi
