#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/pgadmin && bash install.sh install 4
# cd /www/server/mdserver-web/plugins/pgadmin && bash install.sh install 4

install_tmp=${rootPath}/tmp/mw_install.pl

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

# if [ -f ${rootPath}/bin/activate ];then
# 	source ${rootPath}/bin/activate
# fi

Install_pgadmin()
{
	if [ -d $serverPath/pgadmin ];then
		exit 0
	fi

	mkdir -p ${serverPath}/pgadmin
	echo "${1}" > ${serverPath}/pgadmin/version.pl
	
	VER=$1
	
	echo '安装完成'

	cd ${rootPath} && python3 ${rootPath}/plugins/pgadmin/index.py start
		
}

Uninstall_pgadmin()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/pgadmin/index.py stop
	
	rm -rf ${serverPath}/pgadmin
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_pgadmin $2
else
	Uninstall_pgadmin $2
fi
