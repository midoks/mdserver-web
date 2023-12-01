#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl


if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

sysName=`uname`
echo "use system: ${sysName}"

if [ ${sysName} == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
	OSNAME='raspbian'
else
	OSNAME='unknow'
fi




Install_pureftp()
{
	if id ftp &> /dev/null ;then 
	    echo "ftp UID is `id -u ftp`"
	    echo "ftp Shell is `grep "^ftp:" /etc/passwd |cut -d':' -f7 `"
	else
	    groupadd ftp
		useradd -g ftp -s /sbin/nologin ftp
	fi

	# mkdir -p ${serverPath}/pureftp
	mkdir -p ${serverPath}/source/pureftp

	# https://github.com/jedisct1/pure-ftpd/releases/download/1.0.49/pure-ftpd-1.0.49.tar.gz
	# https://download.pureftpd.org/pub/pure-ftpd/releases/pure-ftpd-1.0.49.tar.gz
	

	VER=$1
	DOWNLOAD=https://github.com/jedisct1/pure-ftpd/releases/download/${VER}/pure-ftpd-${VER}.tar.gz
	# DOWNLOAD=https://download.pureftpd.org/pub/pure-ftpd/releases/pure-ftpd-${VER}.tar.gz

	# curl -sSLo pure-ftpd-1.0.49.tar.gz https://download.pureftpd.org/pub/pure-ftpd/releases/pure-ftpd-1.0.49.tar.gz
	if [ ! -f $serverPath/source/pureftp/pure-ftpd-${VER}.tar.gz ];then
		# wget --no-check-certificate -O $serverPath/source/pureftp/pure-ftpd-${VER}.tar.gz $DOWNLOAD
		curl -sSLo $serverPath/source/pureftp/pure-ftpd-${VER}.tar.gz $DOWNLOAD
	fi

	#检测文件是否损坏.
	md5_ok=451879495ba61c1d7dcfca8dd231119f
	if [ -f $serverPath/source/pureftp/pure-ftpd-${VER}.tar.gz ];then
		md5_check=`md5sum $serverPath/source/pureftp/pure-ftpd-${VER}.tar.gz  | awk '{print $1}'`
		if [ "${md5_ok}" == "${md5_check}" ]; then
			echo "pure-ftpd file  check ok"
		fi
	fi

	# Last Download Method
	if [ ! -f $serverPath/source/pureftp/pure-ftpd-${VER}.tar.gz ];then
		wget --no-check-certificate -O $serverPath/source/pureftp/pure-ftpd-${VER}.tar.gz https://dl.midoks.icu/soft/ftp/pure-ftpd-${VER}.tar.gz -T 3
	fi

	if [ ! -d $serverPath/source/pureftp/pure-ftpd-${VER} ];then
		cd $serverPath/source/pureftp  && tar zxvf pure-ftpd-${VER}.tar.gz
	fi

	cd $serverPath/source/pureftp/pure-ftpd-${VER} &&  ./configure --prefix=${serverPath}/pureftp \
　　 	CFLAGS=-O2 \
		--with-puredb \
		--with-quotas \
		--with-cookie \
		--with-virtualhosts \
		--with-diraliases \
		--with-sysquotas \
		--with-ratios \
		--with-altlog \
		--with-paranoidmsg \
		--with-shadow \
		--with-welcomemsg \
		--with-throttling \
		--with-uploadscript \
		--with-language=english \
		--with-rfc2640 \
		--with-ftpwho \
		--with-tls && make && make install && make clean
	
	if [ -d ${serverPath}/pureftp ];then 
		echo "${1}" > ${serverPath}/pureftp/version.pl
		echo '安装完成' > $install_tmp

		cd ${rootPath} && python3 ${rootPath}/plugins/pureftp/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/pureftp/index.py initd_install
	else
		echo '安装失败' > $install_tmp
	fi
}

Uninstall_pureftp()
{
	if [ -f /usr/lib/systemd/system/pureftp.service ];then
		systemctl stop pureftp
		systemctl disable pureftp
		rm -rf /usr/lib/systemd/system/pureftp.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/pureftp/initd/pureftp ];then
		$serverPath/pureftp/initd/pureftp stop
	fi

	rm -rf ${serverPath}/pureftp
	userdel ftp
	groupdel ftp
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_pureftp $2
else
	Uninstall_pureftp $2
fi
