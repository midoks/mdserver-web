#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

function version_gt() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" != "$1"; }
function version_le() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" == "$1"; }
function version_lt() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" != "$1"; }
function version_ge() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" == "$1"; }

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

P_VER=`python3 -V | awk '{print $2}'`
echo "python:$P_VER"

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/pgadmin && bash install.sh install 4
# cd /www/server/mdserver-web/plugins/pgadmin && bash install.sh install 4

# source /www/server/pgadmin/bin/activate
# python /www/server/pgadmin/lib/python3.10/site-packages/pgadmin4/setup.py
# cd /www/server/mdserver-web && python3 plugins/pgadmin/index.py start
# cd /www/server/mdserver-web && python3 plugins/pgadmin/index.py stop

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

Install_pgadmin()
{
	# if [ -d $serverPath/pgadmin ];then
	# 	exit 0
	# fi

	if version_lt "$P_VER" "3.8.0" ;then
		echo 'Python版本太低,无法安装'
	fi
	PG_DIR=${serverPath}/pgadmin
	mkdir -p $PG_DIR
	echo "${1}" > ${serverPath}/pgadmin/version.pl

	if [ ! -f $PG_DIR/bin/activate ];then
	    if version_ge "$P_VER" "3.11.0" ;then
	        echo "python3 > 3.11"
	        cd $PG_DIR && python3 -m venv $PG_DIR
	    else
	        echo "python3 < 3.10"
	        cd $PG_DIR && python3 -m venv .
	    fi
	fi


	if [ -f ${PG_DIR}/bin/activate ];then
		source ${PG_DIR}/bin/activate
	fi

	pip install https://ftp.postgresql.org/pub/pgadmin/pgadmin4/v8.10/pip/pgadmin4-8.10-py3-none-any.whl
	
	VER=$1
	cd ${rootPath} && python3 ${rootPath}/plugins/pgadmin/index.py start

	echo '安装完成'
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
