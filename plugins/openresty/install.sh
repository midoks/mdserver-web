#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/openresty && bash install.sh install 1.21.4.2
# cd /www/server/mdserver-web/plugins/openresty && bash install.sh install 1.21.4.2

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
action=$1
type=$2

VERSION=$2
install_tmp=${rootPath}/tmp/mw_install.pl
openrestyDir=${serverPath}/source/openresty

if id www &> /dev/null ;then 
    echo "www uid is `id -u www`"
    echo "www shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	useradd -g www -s /bin/bash www
fi

if [ "$sysName" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

Install_openresty()
{
	if [ -d $serverPath/openresty ];then
		exit 0
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

	mkdir -p ${openrestyDir}
	echo '正在安装脚本文件...'

	# wget -O openresty-1.21.4.1.tar.gz https://openresty.org/download/openresty-1.21.4.1.tar.gz
	if [ ! -f ${openrestyDir}/openresty-${VERSION}.tar.gz ];then
		wget --no-check-certificate -O ${openrestyDir}/openresty-${VERSION}.tar.gz https://openresty.org/download/openresty-${VERSION}.tar.gz -T 3
	fi

	DOWNLOAD_SIZE=`wc -c ${openrestyDir}/openresty-${VERSION}.tar.gz | awk '{print $1}'`
	if [ "$DOWNLOAD_SIZE" == "0" ];then
		echo 'download failed, download again'
		rm -rf ${openrestyDir}/openresty-${VERSION}.tar.gz
	fi

	# Last Download Method
	if [ ! -f ${openrestyDir}/openresty-${VERSION}.tar.gz ];then
		wget --no-check-certificate -O ${openrestyDir}/openresty-${VERSION}.tar.gz http://dl.midoks.icu/soft/openresty/openresty-${VERSION}.tar.gz -T 3
	fi

	cd ${openrestyDir} && tar -zxvf openresty-${VERSION}.tar.gz

	OPTIONS=''
	if [ "$VERSION" == "1.19.3.1" ]; then
		OPTIONS="${OPTIONS} --with-ipv6"
	fi


	opensslVersion="1.1.1p"
	libresslVersion="3.9.1"
	pcreVersion='8.38'
	if [ "$sysName" == "Darwin" ];then

		if [ ! -f ${openrestyDir}/pcre-${pcreVersion}.tar.gz ];then
			wget --no-check-certificate -O ${openrestyDir}/pcre-${pcreVersion}.tar.gz https://netix.dl.sourceforge.net/project/pcre/pcre/${pcreVersion}/pcre-${pcreVersion}.tar.gz
		fi

		if [ ! -d ${openrestyDir}/pcre-${pcreVersion} ];then
			cd ${openrestyDir} &&  tar -zxvf pcre-${pcreVersion}.tar.gz
		fi
		OPTIONS="${OPTIONS} --with-pcre=${openrestyDir}/pcre-${pcreVersion}"


		if [ ! -f ${openrestyDir}/openssl-${opensslVersion}.tar.gz ];then
	        wget --no-check-certificate -O ${openrestyDir}/openssl-${opensslVersion}.tar.gz https://www.openssl.org/source/openssl-${opensslVersion}.tar.gz
	    fi

	    if [ ! -d ${openrestyDir}/openssl-${opensslVersion} ];then
			cd ${openrestyDir} &&  tar -zxvf openssl-${opensslVersion}.tar.gz
		fi
	    OPTIONS="${OPTIONS} --with-openssl=${openrestyDir}/openssl-${opensslVersion}"

		# BREW_DIR=`which brew`
		# BREW_DIR=${BREW_DIR/\/bin\/brew/}

		# brew info openssl@1.1 | grep /opt/homebrew/Cellar/openssl@1.1 | cut -d \  -f 1 | awk 'END {print}'
		# OPENSSL_LIB_DEPEND_DIR=`brew info openssl@1.1 | grep ${BREW_DIR}/Cellar/openssl@1.1 | cut -d \  -f 1 | awk 'END {print}'`
		# OPTIONS="${OPTIONS} --with-openssl=${OPENSSL_LIB_DEPEND_DIR}"
	else
		if [ ! -f ${openrestyDir}/openssl-${opensslVersion}.tar.gz ];then
	        wget --no-check-certificate -O ${openrestyDir}/openssl-${opensslVersion}.tar.gz https://www.openssl.org/source/openssl-${opensslVersion}.tar.gz
	    fi

	    if [ ! -d ${openrestyDir}/openssl-${opensslVersion} ];then
			cd ${openrestyDir} &&  tar -zxvf openssl-${opensslVersion}.tar.gz
		fi
		OPTIONS="${OPTIONS} --with-openssl=${openrestyDir}/openssl-${opensslVersion}"

		if [ "$VERSION" == "1.25.3.1" ]; then
			OPTIONS="${OPTIONS} --with-http_v3_module"

			if [ ! -f ${openrestyDir}/libressl-${libresslVersion}.tar.gz ];then
		        wget --no-check-certificate -O ${openrestyDir}/libressl-${libresslVersion}.tar.gz https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-${libresslVersion}.tar.gz
		    fi

		    if [ ! -d ${openrestyDir}/libressl-${libresslVersion} ];then
				cd ${openrestyDir} &&  tar -zxvf libressl-${libresslVersion}.tar.gz
			fi
		    
		    OPTIONS="${OPTIONS} --with-cc-opt=-I${openrestyDir}/libressl-${libresslVersion}/libressl/build/include"
		    OPTIONS="${OPTIONS} --with-cc-opt=-I${openrestyDir}/libressl-${libresslVersion}/libressl/build/lib"

		    # --with-cc-opt="-I../libressl/build/include"
    		# --with-ld-opt="-L../libressl/build/lib"
		fi
	fi


	# --with-openssl=$serverPath/source/lib/openssl-1.0.2q
	cd ${openrestyDir}/openresty-${VERSION} && ./configure \
	--prefix=$serverPath/openresty \
	$OPTIONS \
	--with-stream \
	--with-http_v2_module \
	--with-http_ssl_module  \
	--with-http_slice_module \
	--with-http_stub_status_module \
	--with-http_sub_module \
	--with-http_realip_module
	# --without-luajit-gc64
	# --with-debug
	# 用于调式

	CMD_MAKE=`which gmake`
	if [ "$?" == "0" ];then
		gmake -j${cpuCore} && gmake install && gmake clean
	else
		make -j${cpuCore} && make install && make clean
	fi

	if [ -d $serverPath/openresty ];then
		echo "${VERSION}" > $serverPath/openresty/version.pl

		mkdir -p $serverPath/web_conf/php/conf
		echo 'set $PHP_ENV 0;' > $serverPath/web_conf/php/conf/enable-php-00.conf

		#初始化 
		cd ${rootPath} && python3 ${rootPath}/plugins/openresty/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/openresty/index.py initd_install
		rm -rf $openrestyDir/openresty-${VERSION}
    fi

    if [ -d ${openrestyDir}/pcre-${pcreVersion} ];then
    	rm -rf ${openrestyDir}/pcre-${pcreVersion}
    fi

    if [ -d ${openrestyDir}/openssl-${opensslVersion} ];then
    	rm -rf ${openrestyDir}/openssl-${opensslVersion}
    fi

    if [ -d ${openrestyDir}/libressl-${libresslVersion} ];then
    	rm -rf ${openrestyDir}/libressl-${libresslVersion}
    fi
	echo '安装完成'
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
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_openresty
else
	Uninstall_openresty
fi
