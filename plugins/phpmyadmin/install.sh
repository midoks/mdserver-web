#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl


if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

if [ "$sys_os" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

sysName=`uname`
echo "use system: ${sysName}"

if [ "${sysName}" == "Darwin" ]; then
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

Install_phpmyadmin()
{
	if [ -d $serverPath/phpmyadmin ];then
		exit 0
	fi

	mkdir -p ${serverPath}/phpmyadmin
	mkdir -p ${serverPath}/source/phpmyadmin
	echo "${1}" > ${serverPath}/phpmyadmin/version.pl
	
	VER=$1
	
	FDIR=phpMyAdmin-${VER}-all-languages
	FILE=phpMyAdmin-${VER}-all-languages.tar.gz
	DOWNLOAD=https://files.phpmyadmin.net/phpMyAdmin/${VER}/$FILE
	

	if [ ! -f $serverPath/source/phpmyadmin/$FILE ];then
		wget --no-check-certificate -O $serverPath/source/phpmyadmin/$FILE $DOWNLOAD
	fi

	if [ ! -d $serverPath/source/phpmyadmin/$FDIR ];then
		cd $serverPath/source/phpmyadmin  && tar zxvf $FILE
	fi

	cp -r $serverPath/source/phpmyadmin/$FDIR $serverPath/phpmyadmin/
	cd $serverPath/phpmyadmin/ && mv $FDIR phpmyadmin
	rm -rf $serverPath/source/phpmyadmin/$FDIR
	
	echo '安装完成'

	cd ${rootPath} && python3 ${rootPath}/plugins/phpmyadmin/index.py start
		
}

Uninstall_phpmyadmin()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/phpmyadmin/index.py stop
	
	rm -rf ${serverPath}/phpmyadmin
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_phpmyadmin $2
else
	Uninstall_phpmyadmin $2
fi
