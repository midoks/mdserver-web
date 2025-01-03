#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# https://dev.mysql.com/downloads/mysql/
# https://downloads.mysql.com/archives/community/

# SHOW VARIABLES LIKE 'default_authentication_plugin';
# SELECT user, host, plugin FROM mysql.user;
# default_authentication_plugin=caching_sha2_password

# /www/server/mysql-community/bin/mysqld --basedir=/www/server/mysql-community --datadir=/www/server/mysql-community/data --initialize-insecure --explicit_defaults_for_timestamp

# source bin/activate
# cd /www/server/mdserver-web/plugins/mysql-community && bash install.sh install 9.0
# cd /www/server/mdserver-web/plugins/mysql-community && bash install.sh uninstall 9.0
# cd /www/server/mdserver-web && python3 plugins/mysql-community/index.py start 8.0
# cd /www/server/mdserver-web && python3 plugins/mysql-community/index.py fix_db_access
# cd /www/server/mdserver-web && python3 plugins/mysql/index.py do_full_sync  {"db":"xxx","sign":"","begin":1}

action=$1
type=$2

if id mysql &> /dev/null ;then 
    echo "mysql UID is `id -u mysql`"
    echo "mysql Shell is `grep "^mysql:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd mysql
	useradd -g mysql -s /usr/sbin/nologin mysql
fi


_os=`uname`
echo "use system: ${_os}"
if [ ${_os} == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eq "openSUSE" /etc/*-release; then
	OSNAME='opensuse'
elif grep -Eq "FreeBSD" /etc/*-release; then
	OSNAME='freebsd'
elif grep -Eqi "Arch" /etc/issue || grep -Eq "Arch" /etc/*-release; then
	OSNAME='arch'
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
elif grep -Eqi "Rocky" /etc/issue || grep -Eq "Rocky" /etc/*-release; then
	OSNAME='rocky'
elif grep -Eqi "AlmaLinux" /etc/issue || grep -Eq "AlmaLinux" /etc/*-release; then
	OSNAME='alma'
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
else
	OSNAME='unknow'
fi

VERSION_ID=`cat /etc/*-release | grep 'VERSION_ID' | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

# 针对ubuntu24进行优化
if [[ "$OSNAME" == "ubuntu" ]] && [[ "$VERSION_ID" =~ "24" ]]; then
	cur_dir=`pwd`
	cd /usr/lib/x86_64-linux-gnu
	if [ ! -f libaio.so.1 ];then
		ln -s libaio.so.1t64.0.2 libaio.so.1
	fi

	if [ ! -f libncurses.so.6 ];then
		ln -s libncursesw.so.6.4 libncurses.so.6
	fi
	cd $cur_dir
fi

if [ "${2}" == "" ];then
	echo '缺少安装脚本...'
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...'
	exit 0
fi

if [ "${action}" == "uninstall" ];then
	
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-community/index.py stop ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-community/index.py initd_uninstall ${type}
	cd $curPath

	if [ -f /usr/lib/systemd/system/mysql-community.service ] || [ -f /lib/systemd/system/mysql-community.service ];then
		systemctl stop mysql-community
		systemctl disable mysql-community
		rm -rf /usr/lib/systemd/system/mysql-community.service
		rm -rf /lib/systemd/system/mysql-community.service
		systemctl daemon-reload
	fi
fi


sh -x $curPath/versions/$2/install_generic.sh $1

if [ "${action}" == "install" ];then
	#初始化

	if [ "$?" != "0" ];then
		exit $?
	fi
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-community/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/mysql-community/index.py initd_install ${type}
fi
