#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=1.0
sysName=`uname`

# bash install.sh install 1.0
# cd /www/server/mdserver-web/plugins/ollama && bash install.sh install 1.0
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/ollama && bash install.sh install 1.0

bash ${rootPath}/scripts/getos.sh



OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


ARCH="amd64"

get_arch() {
	TMP_ARCH=`arch`
	if [ "$TMP_ARCH" == "x86_64" ];then
		ARCH="amd64"
	elif [ "$TMP_ARCH" == "aarch64" ];then
		ARCH="arm64"
	else
		echo $ARCH
	fi
}

Install_App()
{
	curl -fsSL https://ollama.com/install.sh | sh

	mkdir -p $serverPath/ollama
	echo "$VERSION" > $serverPath/ollama/version.pl
	echo 'install successful'
}

Uninstall_App()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/ollama/index.py stop

	systemctl disable ollama.service
	rm -rf /etc/systemd/system/ollama.service
	systemctl daemon-reload
	rm -rf $(which ollama)
	rm -rf /usr/share/ollama
	rm -rf ~/.ollama

	userdel ollama
	groupdel ollama

	if command -v apt &> /dev/null; then
		apt remove -y ollama
	fi

	rm -rf $serverPath/ollama
	echo "install fail"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
