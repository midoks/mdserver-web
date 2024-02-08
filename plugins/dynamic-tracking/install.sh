#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/dynamic-tracking && /bin/bash install.sh uninstall 1.0
# cd /www/server/mdserver-web/plugins/dynamic-tracking && /bin/bash install.sh install 1.0

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi


OSNAME=`bash ${rootPath}/scripts/getos.sh`

if [ "" == "$OSNAME" ];then
	OSNAME=`cat ${rootPath}/data/osname.pl`
fi

if [ "macos" != "$OSNAME" ];then
	SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
fi

Install_App()
{

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	mkdir -p $serverPath/dynamic-tracking

	cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
	HTTP_PREFIX="https://"
	if [ ! -z "$cn" ];then
	    HTTP_PREFIX="https://mirror.ghproxy.com/"
	fi
	
	# FlameGraph start
	if [ ! -d $serverPath/dynamic-tracking/FlameGraph ];then
		if [ ! -f $serverPath/source/FlameGraph.zip ]; then
	    	wget --no-check-certificate -O $serverPath/source/FlameGraph.zip ${HTTP_PREFIX}github.com/brendangregg/FlameGraph/archive/refs/heads/master.zip
		fi

		cd $serverPath/source && unzip $serverPath/source/FlameGraph.zip
		mv $serverPath/source/FlameGraph-master $serverPath/dynamic-tracking/FlameGraph
	fi
	# FlameGraph end

	

	shell_file=${curPath}/versions/${OSNAME}.sh
	echo $shell_file
	if [ ! -f $shell_file ];then
		echo '不支持...' > $install_tmp 
		exit 1
	fi
	
	bash -x $shell_file

	echo "cp -rf ${curPath}/shell $serverPath/dynamic-tracking"
	cp -rf ${curPath}/shell $serverPath/dynamic-tracking

	echo "${VERSION}" > $serverPath/dynamic-tracking/version.pl
	echo '安装完成' > $install_tmp

	cd ${rootPath} && python3 ${rootPath}/plugins/dynamic-tracking/index.py start
	# cd ${rootPath} && python3 ${rootPath}/plugins/dynamic-tracking/index.py initd_install

}

Uninstall_App()
{
	rm -rf $serverPath/dynamic-tracking
	echo "Uninstall_App" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
