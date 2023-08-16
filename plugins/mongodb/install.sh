#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4
# cd /www/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

sysName=`uname`
echo "use system: ${sysName}"

OSNAME=`bash ${rootPath}/scripts/getos.sh`
if [ "macos" != "$OSNAME" ];then
	SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
fi

Install_app()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

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
		echo '安装完成' > $install_tmp

		#初始化 
		cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py initd_install
	fi
}

Uninstall_app()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py stop
	rm -rf $serverPath/mongodb
	echo "Uninstall_mongodb" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app
else
	Uninstall_app
fi
