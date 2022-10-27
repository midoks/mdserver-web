#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


action=$1
type=$2

VERSION=$2
install_tmp=${rootPath}/tmp/mw_install.pl
openrestyDir=${serverPath}/source/openresty

if id www &> /dev/null ;then 
    echo "www UID is `id -u www`"
    echo "www Shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	# useradd -g www -s /sbin/nologin www
	useradd -g www -s /bin/bash www
fi

Install_openresty()
{
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
	# ----- cpu end ------

	mkdir -p ${openrestyDir}
	echo '正在安装脚本文件...' > $install_tmp

	if [ ! -f ${openrestyDir}/openresty-${VERSION}.tar.gz ];then
		wget -O ${openrestyDir}/openresty-${VERSION}.tar.gz https://openresty.org/download/openresty-${VERSION}.tar.gz
	fi


	cd ${openrestyDir} && tar -zxvf openresty-${VERSION}.tar.gz

	# --with-openssl=$serverPath/source/lib/openssl-1.0.2q
	cd ${openrestyDir}/openresty-${VERSION} && ./configure \
	--prefix=$serverPath/openresty \
	--with-ipv6 \
	--with-stream \
	--with-http_v2_module \
	--with-http_ssl_module  \
	--with-http_slice_module \
	--with-http_stub_status_module \
	--with-http_realip_module
	# --without-luajit-gc64
	# --with-debug
	# 用于调式

	make -j${cpuCore} && make install && make clean

	if [ -d $serverPath/openresty ];then
		echo "${VERSION}" > $serverPath/openresty/version.pl

		mkdir -p $serverPath/web_conf/php/conf
		echo 'set $PHP_ENV 0;' > $serverPath/web_conf/php/conf/enable-php-00.conf

		#初始化 
		cd ${rootPath} && python3 ${rootPath}/plugins/openresty/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/openresty/index.py initd_install
    fi
	echo '安装完成' > $install_tmp
}

Uninstall_openresty()
{

	if [ -f /usr/lib/systemd/system/openresty.service ] || [ -f /lib/systemd/system/openresty.service ];then
		systemctl stop openresty
		rm -rf /usr/systemd/system/openresty.service
		rm -rf /lib/systemd/system/openresty.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/openresty/init.d/openresty ];then
		$serverPath/openresty/init.d/openresty stop
	fi

	rm -rf $serverPath/openresty
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_openresty
else
	Uninstall_openresty
fi
