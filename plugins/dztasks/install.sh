#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/dztasks && bash install.sh install 1.0
# cd /wwww/server/mdserver-web/plugins/dztasks && bash install.sh install 1.0
VERSION=$2
sysArch=`arch`
sysName=`uname`

DZ_ARCH_NAME=amd64
if [ "$sysArch" == "arm64" ];then
	DZ_ARCH_NAME=arm64
elif [ "$sysArch" == "x86_64" ]; then
	DZ_ARCH_NAME=amd64
elif [ "$sysArch" == "aarch64" ]; then
	DZ_ARCH_NAME=aarch64
fi

DZ_NAME=linux
if [ "$sysName" == "Darwin" ];then
	DZ_NAME=darwin
fi
Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source
	mkdir -p $serverPath/source/dztasks
	mkdir -p $serverPath/dztasks

	FILE_TGZ=dztasks_v${VERSION}_${DZ_NAME}_${DZ_ARCH_NAME}.tar.gz
	DZ_DIR=$serverPath/source/dztasks

	echo $FILE_TGZ
	# https://github.com/midoks/dztasks/releases/download/1.0/dztasks_v1.0_darwin_amd64.tar.gz
	if [ ! -f $DZ_DIR/${FILE_TGZ} ];then
		wget --no-check-certificate -O $DZ_DIR/${FILE_TGZ} https://github.com/midoks/dztasks/releases/download/${VERSION}/${FILE_TGZ}
	fi

	cd $DZ_DIR && tar -zxvf ${FILE_TGZ} -C $serverPath/dztasks
	echo "${VERSION}" > $serverPath/dztasks/version.pl
	cd ${rootPath} && python3 ${rootPath}/plugins/dztasks/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/dztasks/index.py initd_install

	echo '安装dztasks成功!'
}

Uninstall_App()
{
	if [ -f /usr/lib/systemd/system/dztasks.service ];then
		systemctl stop dztasks
		systemctl disable dztasks
		rm -rf /usr/lib/systemd/system/dztasks.service
		systemctl daemon-reload
	fi

	if [ -f /lib/systemd/system/dztasks.service ];then
		systemctl stop dztasks
		systemctl disable dztasks
		rm -rf /lib/systemd/system/dztasks.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/dztasks/initd/dztasks ];then
		$serverPath/dztasks/initd/dztasks stop
	fi

	if [ -d $serverPath/dztasks ];then
		rm -rf $serverPath/dztasks
	fi
	
	echo "卸载dztasks成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
