#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

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
	mkdir -p ${serverPath}/pureftp
	mkdir -p ${serverPath}/source/pureftp

	VER=$1
	FILE=pure-ftpd-${VER}.tar.gz
	FDIR=pure-ftpd-${VER}
	DOWNLOAD=https://download.pureftpd.org/pub/pure-ftpd/releases/$FILE
	

	if [ ! -f $serverPath/source/pureftp/$FILE ];then
		wget -O $serverPath/source/pureftp/$FILE $DOWNLOAD
	fi

	if [ ! -d $serverPath/source/pureftp/$FDIR ];then
		cd $serverPath/source/pureftp  && tar zxvf $FILE
	fi

	cd $serverPath/source/pureftp/$FDIR &&  ./configure --prefix=${serverPath}/pureftp \
　　 	--with-everything && make && make install && make clean
	
	echo "${1}" > ${serverPath}/pureftp/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_pureftp()
{
	rm -rf ${serverPath}/pureftp
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_pureftp $2
else
	Uninstall_pureftp $2
fi
