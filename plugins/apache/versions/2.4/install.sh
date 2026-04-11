#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/apache && bash install.sh install 2.4
# cd /www/server/mdserver-web/plugins/apache && bash install.sh install 2.4

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
action=$1
type=$2

VERSION=2.4.66
apacheDir=${serverPath}/source/apache

Install_App()
{
	if [ "${action}" == "install" ];then
		if [ -d $serverPath/apache ];then
			exit 0
		fi
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

	mkdir -p ${apacheDir}
	echo 'install script ...'
	OPTIONS=''

	# 安装 APR 和 APR-util
	APR_VERSION=1.7.6
	APR_UTIL_VERSION=1.6.3

	if [ ! -f ${apacheDir}/apr-${APR_VERSION}.tar.bz2 ];then
		wget --no-check-certificate -O ${apacheDir}/apr-${APR_VERSION}.tar.bz2 https://downloads.apache.org/apr/apr-${APR_VERSION}.tar.bz2 -T 3
	fi

	if [ ! -f ${apacheDir}/apr-util-${APR_UTIL_VERSION}.tar.bz2 ];then
		wget --no-check-certificate -O ${apacheDir}/apr-util-${APR_UTIL_VERSION}.tar.bz2 https://downloads.apache.org/apr/apr-util-${APR_UTIL_VERSION}.tar.bz2 -T 3
	fi

	# 安装 APR
	if [ ! -d ${serverPath}/apache/apr ];then
		cd ${apacheDir} && tar -jxf apr-${APR_VERSION}.tar.bz2
		cd ${apacheDir}/apr-${APR_VERSION} && ./configure --prefix=${serverPath}/apache/apr
		make -j${cpuCore} && make install
		if [ "$?" == "0" ];then
					# 检查 APR 配置文件
					APR_CONFIG=$(find ${serverPath}/apache/apr -name "apr-*config" | head -1)
					if [ -z "$APR_CONFIG" ];then
						echo "APR installation failed: apr-config not found"
						exit 1
					fi
					echo "APR installed successfully: $APR_CONFIG"
				else
					echo "APR configure failed"
					exit 1
				fi
	fi

	# 安装 APR-util
	if [ ! -d ${serverPath}/apache/apr-util ];then
		cd ${apacheDir} && tar -jxf apr-util-${APR_UTIL_VERSION}.tar.bz2
		cd ${apacheDir}/apr-util-${APR_UTIL_VERSION} && ./configure --prefix=${serverPath}/apache/apr-util --with-apr=${serverPath}/apache/apr
		make -j${cpuCore} && make install
		if [ "$?" == "0" ];then
					# 检查 APR-util 配置文件
					APU_CONFIG=$(find ${serverPath}/apache/apr-util -name "apu-*config" | head -1)
					if [ -z "$APU_CONFIG" ];then
						echo "APR-util installation failed: apu-config not found"
						find ${serverPath}/apache/apr-util -name "apu-*config"
						exit 1
					fi
					echo "APR-util installed successfully: $APU_CONFIG"
				else
					echo "APR-util configure failed"
					exit 1
				fi
	fi

	if [ ! -f ${apacheDir}/httpd-${VERSION}.tar.bz2 ];then
		wget --no-check-certificate -O ${apacheDir}/httpd-${VERSION}.tar.bz2 https://downloads.apache.org/httpd/httpd-${VERSION}.tar.bz2 -T 3
	fi

	if [ ! -d ${apacheDir}/httpd-${VERSION} ];then
		cd ${apacheDir} && tar -jxf ${apacheDir}/httpd-${VERSION}.tar.bz2
	fi
	

	# 检查 APR 和 APR-util 可执行文件
	APR_CONFIG=$(find ${serverPath}/apache/apr -name "apr-*config" | head -1)
	APU_CONFIG=$(find ${serverPath}/apache/apr-util -name "apu-*config" | head -1)

	if [ -z "$APR_CONFIG" ];then
		echo "APR config not found"
		exit 1
	fi

	if [ -z "$APU_CONFIG" ];then
		echo "APR-util config not found"
		exit 1
	fi

	OPTIONS="${OPTIONS} --with-apr=$APR_CONFIG"
	OPTIONS="${OPTIONS} --with-apr-util=$APU_CONFIG"

	if [ "$sysName" != "Darwin" ];then
		OPTIONS="${OPTIONS} --enable-systemd"
	fi
	# echo "cd ${apacheDir}/httpd-${VERSION} && ./configure --prefix=$serverPath/apache $OPTIONS"
	cd ${apacheDir}/httpd-${VERSION} && ./configure \
	--prefix=$serverPath/apache/httpd \
	$OPTIONS

	make -j${cpuCore} && make install && make clean


	if [ -d ${apacheDir}/apr-${APR_VERSION} ];then
    	rm -rf ${apacheDir}/apr-${APR_VERSION}
    fi

    if [ -d ${apacheDir}/apr-util-${APR_UTIL_VERSION} ];then
    	rm -rf ${apacheDir}/apr-util-${APR_UTIL_VERSION}
    fi

    if [ -d ${apacheDir}/httpd-${APR_UTIL_VERSION} ];then
    	rm -rf ${apacheDir}/httpd-${APR_UTIL_VERSION}
    fi

	echo 'installation of apache completed'
}

Uninstall_App()
{
	echo 'uninstalling apache completed'
}

action=$1
if [ "${1}" == "install" ];then
	Install_App
elif [ "${1}" == "upgrade" ];then
	Install_App
else
	Uninstall_App
fi
