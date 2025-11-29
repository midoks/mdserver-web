#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi


# cd /www/server/mdserver-web/plugins/doh && bash install.sh install 0.9.15

# 详细状态信息
# sudo systemctl status doh -l
# 查看完整日志
# sudo journalctl -u doh -n 100
# 实时日志跟踪
# sudo journalctl -u doh -f


URL_DOWNLOAD=https://github.com/DNSCrypt/doh-server/releases/download


bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

Install_App()
{

	mkdir -p $serverPath/source/doh

	echo '正在安装脚本文件...'
	version=$1

	if [ "macos" == "$OSNAME" ];then
		echo "not support!"
		exit
	else
		file=doh-proxy_${version}_linux-x86_64
	fi

	# https://github.com/DNSCrypt/doh-server/releases/download/0.9.15/doh-proxy_0.9.15_linux-aarch64.tar.bz2
	file_xz="${file}.tar.bz2"
	echo "wget -O $serverPath/source/doh/$file_xz ${URL_DOWNLOAD}/${version}/${file_xz}"
	if [ ! -f $serverPath/source/doh/$file_xz ];then
		wget  --no-check-certificate -O $serverPath/source/doh/$file_xz ${URL_DOWNLOAD}/${version}/${file_xz}
	fi

	cd $serverPath/source/doh && xz -k -d $file_xz
	if [ -f $file ];then
		mkdir -p $serverPath/doh
		mv $serverPath/source/doh/$file $serverPath/doh/doh
	fi


	if [ -d $serverPath/doh ];then
		echo $version > $serverPath/doh/version.pl

		cd ${rootPath} && python3 plugins/doh/index.py start
		cd ${rootPath} && python3 plugins/doh/index.py initd_install
	fi

	echo 'install doh success'
}

Uninstall_App()
{

	if [ -f /usr/lib/systemd/system/doh.service ];then
		systemctl stop doh
		systemctl disable doh
		rm -rf /usr/lib/systemd/system/doh.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/doh/initd/doh ];then
		$serverPath/doh/initd/doh stop
	fi

	rm -rf $serverPath/doh
	echo 'uninstall doh success'
}


action=$1
version=$2
if [ "${1}" == 'install' ];then
	Install_App $version
else
	Uninstall_App $version
fi
