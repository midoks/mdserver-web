#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/phpldapadmin && bash install.sh install 1.2.6.7
# cd /www/server/mdserver-web && python3 plugins/phpldapadmin/index.py start

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
	if [ -d $serverPath/phpldapadmin ];then
		exit 0
	fi

	mkdir -p ${serverPath}/phpldapadmin
	mkdir -p ${serverPath}/source/phpldapadmin
	echo "${1}" > ${serverPath}/phpldapadmin/version.pl
	
	VER=$1

	# https://github.com/leenooks/phpLDAPadmin/archive/refs/tags/1.2.6.7.tar.gz
	FDIR=phpLDAPadmin-${VER}
	FILE=${VER}.tar.gz
	DOWNLOAD=https://github.com/leenooks/phpLDAPadmin/archive/refs/tags/${FILE}
	

	if [ ! -f $serverPath/source/phpmyadmin/$FILE ];then
		wget --no-check-certificate -O $serverPath/source/phpldapadmin/$FILE $DOWNLOAD
	fi

	if [ ! -d $serverPath/source/phpldapadmin/$FDIR ];then
		cd $serverPath/source/phpldapadmin  && tar zxvf $FILE
	fi

	cp -r $serverPath/source/phpldapadmin/$FDIR $serverPath/phpldapadmin/
	cd $serverPath/phpldapadmin/ && mv $FDIR phpldapadmin
	# rm -rf $serverPath/source/phpldapadmin/$FDIR
	
	cd ${rootPath} && python3 ${rootPath}/plugins/phpldapadmin/index.py start
	echo '安装完成'
		
}

Uninstall_App()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/phpldapadmin/index.py stop
	
	rm -rf ${serverPath}/phpldapadmin
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App $2
else
	Uninstall_App $2
fi
