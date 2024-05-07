#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# https://www.mongodb.com/try/download/community

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 7.0
# cd /www/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 7.0
# cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mongodb/index.py start



curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

sysName=`uname`
echo "use system: ${sysName}"

OSNAME=`bash ${rootPath}/scripts/getos.sh`

if [ "" == "$OSNAME" ];then
	OSNAME=`cat ${rootPath}/data/osname.pl`
fi

if [ "macos" != "$OSNAME" ];then
	SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
fi

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi
Install_app()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	# if id mongodb &> /dev/null ;then 
	#     echo "mongodb uid is `id -u mongodb`"
	#     echo "mongodb shell is `grep "^mongodb:" /etc/passwd |cut -d':' -f7 `"
	# else
	#     groupadd mongodb
	# 	useradd -g mongodb mongodb
	# fi

	# if [ "centos" == "$OSNAME" ];then
	# 	OSNAME=rhel
	# fi

	# if [ "fedora" == "$OSNAME" ];then
	# 	OSNAME=rhel
	# fi

	# if [ "rocky" == "$OSNAME" ];then
	# 	OSNAME=rhel
	# fi

	cd ${rootPath}/plugins/php/lib && /bin/bash openssl_11.sh

	shell_file=${curPath}/versions/${VERSION}/${OSNAME}.sh

	if [ -f $shell_file ];then
		bash -x $shell_file
	else
		echo '不支持...' > $install_tmp 
		exit 1
	fi

	if [ "$?" == "0" ];then
		mkdir -p $serverPath/mongodb
		echo "${VERSION}" > $serverPath/mongodb/version.pl
		echo 'mongodb安装完成'

		#初始化 
		cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py initd_install
	fi
}

Uninstall_app()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py stop
	rm -rf $serverPath/mongodb


	if [ -f /usr/lib/systemd/system/mongodb.service ] || [ -f /lib/systemd/system/mongodb.service ];then
		systemctl stop mongodb
		systemctl disable mongodb
		rm -rf /usr/lib/systemd/system/mongodb.service
		rm -rf /lib/systemd/system/mongodb.service
		systemctl daemon-reload
	fi

	echo 'mongodb卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app
else
	Uninstall_app
fi
