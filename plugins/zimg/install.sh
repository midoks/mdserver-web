#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


zimgSourceDir=${serverPath}/source/zimg

install_tmp=${rootPath}/tmp/mw_install.pl


sysName=`uname`
echo "use system: ${sysName}"
if [ ${sysName} == "Darwin" ]; then
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



# install package
if [ "${OSNAME}" == "centos" ] || [ "${OSNAME}" == "fedora" ]; then
	yum install nasm -y
fi

if [ "${OSNAME}" == "debian" ] || [ "${OSNAME}" == "ubuntu" ]; then
	apt install nasm -y
fi

Install_libjpeg_turbo(){
	mkdir -p $zimgSourceDir/libjpeg-turbo
	cd $zimgSourceDir/libjpeg-turbo
	if [ ! -d $zimgSourceDir/libjpeg-turbo ];then
		wget https://downloads.sourceforge.net/project/libjpeg-turbo/1.3.1/libjpeg-turbo-1.3.1.tar.gz
		tar zxvf libjpeg-turbo-1.3.1.tar.gz
		cd libjpeg-turbo-1.3.1
		./configure --prefix=/usr/local --with-jpeg8
		make && make install
	fi 
}

Install_zimg_source(){
	mkdir -p $zimgSourceDir
	cd $zimgSourceDir
	if [ ! -d $zimgSourceDir/zimg ];then
		git clone https://github.com/buaazp/zimg -b master --depth=1
		cd zimg
		make
	fi
	if [ -f $zimgSourceDir/zimg/bin/zimg ];then
		cp -r $zimgSourceDir/zimg/bin $serverPath/zimg
	fi
}

Install_zimg()
{
	isStart=""
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/zimg
	echo '1.0' > $serverPath/zimg/version.pl

	if [ "macos" == "${OSNAME}" ];then
		echo 'macosx unavailable' > $install_tmp
	else
		if [ ! -f $serverPath/zimg/bin ];then
			Install_libjpeg_turbo
			Install_zimg_source
		fi
	fi

	echo 'Install complete' > $install_tmp
}

Uninstall_zimg()
{
	rm -rf $serverPath/zimg
	echo "Uninstall completed" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_zimg
else
	Uninstall_zimg
fi
