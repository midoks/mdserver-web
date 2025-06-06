#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/lam && bash install.sh install 9.0
# cd /www/server/mdserver-web && python3 plugins/lam/index.py start

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

Install_App()
{
	if [ -d $serverPath/lam ];then
		exit 0
	fi

	mkdir -p ${serverPath}/lam
	mkdir -p ${serverPath}/source/lam
	echo "${1}" > ${serverPath}/lam/version.pl
	
	VER=$1

	# https://github.com/LDAPAccountManager/lam/releases/download/9.0/ldap-account-manager-9.0.tar.bz2
	FDIR=ldap-account-manager-${VER}
	FILE=ldap-account-manager-${VER}.tar.bz2
	DOWNLOAD=https://github.com/LDAPAccountManager/lam/releases/download/9.0/${FILE}
	

	if [ ! -f $serverPath/source/phpmyadmin/$FILE ];then
		wget --no-check-certificate -O $serverPath/source/lam/$FILE $DOWNLOAD
	fi

	if [ ! -d $serverPath/source/lam/$FDIR ];then
		cd $serverPath/source/lam  && tar jxvf $FILE
	fi

	cp -r $serverPath/source/lam/$FDIR $serverPath/lam/
	cd $serverPath/lam/ && mv $FDIR lam
	# rm -rf $serverPath/source/lam/$FDIR
	
	cd ${rootPath} && python3 ${rootPath}/plugins/lam/index.py start
	echo '安装完成'
		
}

Uninstall_App()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/lam/index.py stop
	
	rm -rf ${serverPath}/lam
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App $2
else
	Uninstall_App $2
fi
