#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source
sysName=`uname`

SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

VERSION=$2

sysArch=`arch`
sysName=`uname`

ARCH_NAME=amd64
if [ "$sysArch" == "arm64" ];then
	ARCH_NAME=arm64
elif [ "$sysArch" == "x86_64" ]; then
	ARCH_NAME=amd64
elif [ "$sysArch" == "aarch64" ]; then
	ARCH_NAME=aarch64
fi

FILE_TGZ=loki-linux-${ARCH_NAME}.zip

# 检查是否通
Install_App()
{
	SourceDir=$serverPath/source/grafana
	InstallDir=$serverPath/loki
	mkdir -p ${SourceDir}
	mkdir -p ${InstallDir}

	if [ ! -f ${SourceDir}/${FILE_TGZ} ];then
		wget --no-check-certificate -O ${SourceDir}/${FILE_TGZ} https://github.com/grafana/loki/releases/download/v${VERSION}/${FILE_TGZ}
	fi

	if [ ! -d $InstallDir/bin/loki ];then
		cd ${SourceDir} && unzip ${FILE_TGZ}
		mkdir -p $InstallDir/bin
		cp -rf ./loki-linux-${ARCH_NAME} $InstallDir/bin/loki
		rm -rf ./loki-linux-${ARCH_NAME}
	fi
}

Uninstall_App()
{
	echo "卸载成功"
}

# StandardOutput=syslog
# StandardError=syslog
# SyslogIdentifier=loki

# # 资源限制 (根据服务器配置调整)
# MemoryLimit=1G
# CPUQuota=200%

action=${1}
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
