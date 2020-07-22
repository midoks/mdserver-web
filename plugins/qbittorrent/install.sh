#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/bt_install.pl

#https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

Install_mac_ffmpeg()
{
	macVer='ffmpeg-20200721-b5f1e05-macos64-static'
	if [ ! -f $serverPath/source/${macVer}.zip ];then
		wget -O $serverPath/source/${macVer}.zip https://ffmpeg.zeranoe.com/builds/macos64/static/${macVer}.zip
	fi

	if [ ! -d $serverPath/lib/ffmpeg ];then
		cd $serverPath/source && unzip $serverPath/source/${macVer}.zip
		mv ${macVer} $serverPath/lib/ffmpeg
	fi
}

Install_linux_ffmpeg()
{
	if [ ! -f $serverPath/source/ffmpeg-release-amd64-static.tar.xz ];then
		wget -O $serverPath/source/ffmpeg-release-amd64-static.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
	fi

	if [ ! -d $serverPath/lib/ffmpeg ];then
		cd $serverPath/source && tar -xvf $serverPath/source/ffmpeg-release-amd64-static.tar.xz
		#mkdir -p $serverPath/lib/ffmpeg
		mv ffmpeg-4.3-amd64-static $serverPath/lib/ffmpeg
	fi
}

Install_qbittorrent()
{
	if [ $sysName == 'Darwin' ]; then
		Install_mac_ffmpeg
	else
		yum -y install qbittorrent-nox
		#qbittorrent-nox -d

		Install_linux_ffmpeg
	fi

	# pip install python-qbittorrent==0.4.2
	pip install python-qbittorrent==0.3

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/qbittorrent

	QB_DIR=${serverPath}/source/qbittorrent
	mkdir -p $QB_DIR

	echo '4.1.5' > $serverPath/qbittorrent/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_qbittorrent()
{
	rm -rf $serverPath/qbittorrent
	which yum && yum -y remove qbittorrent-nox
	echo "Uninstall_qbittorrent" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_qbittorrent
else
	Uninstall_qbittorrent
fi
