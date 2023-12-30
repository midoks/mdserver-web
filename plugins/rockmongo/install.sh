#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl


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
	# if [ -d $serverPath/rockmongo ];then
	# 	exit 0
	# fi

	mkdir -p ${serverPath}/rockmongo
	mkdir -p ${serverPath}/source/rockmongo
	echo "${1}" > ${serverPath}/rockmongo/version.pl
	
	VER=$1

	FDIR=rockmongo-${VER}
	FILE=${VER}.tar.gz

	DOWNLOAD=https://github.com/iwind/rockmongo/archive/refs/tags/${VER}.tar.gz
	

	if [ ! -f $serverPath/source/rockmongo/$FILE ];then
		wget --no-check-certificate -O $serverPath/source/rockmongo/$FILE $DOWNLOAD
		echo "wget --no-check-certificate -O $serverPath/source/rockmongo/$FILE $DOWNLOAD"
	fi

	if [ ! -d $serverPath/source/rockmongo/$FDIR ];then
		cd $serverPath/source/rockmongo  && tar zxvf $FILE
	fi

	cp -r $serverPath/source/rockmongo/$FDIR $serverPath/rockmongo/
	cd $serverPath/rockmongo/ && mv $FDIR rockmongo
	rm -rf $serverPath/source/rockmongo/$FDIR
	
	cd ${rootPath} && python3 ${rootPath}/plugins/rockmongo/index.py start
	echo '安装完成'
}

Uninstall_App()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/rockmongo/index.py stop
	
	rm -rf ${serverPath}/rockmongo
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App $2
else
	Uninstall_App $2
fi
