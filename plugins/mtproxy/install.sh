#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysArch=`arch`
sysName=`uname`


# cd /www/server/mdserver-web && python3 plugins/mtproxy/index.py url
# cd /www/server/mdserver-web/plugins/mtproxy && /bin/bash install.sh install 1.0

bash ${rootPath}/scripts/getos.sh
echo "bash ${rootPath}/scripts/getos.sh"
OSNAME=`cat ${rootPath}/data/osname.pl`

VERSION_MIN=2.1.7
VERSION=v${VERSION_MIN}

sysName=$(uname | tr '[:upper:]' '[:lower:]')

ARCH=amd64
get_arch() {
	echo "package main
import (
	\"fmt\"
	\"runtime\"
)
func main() { fmt.Println(runtime.GOARCH) }" > /tmp/go_arch.go

	ARCH=$(go run /tmp/go_arch.go)
	echo "ARCH:${ARCH}"
}

TARGET_DIR="${serverPath}/mtproxy"

get_download_url() {
	DOWNLOAD_URL="https://github.com/9seconds/mtg/releases/download/$VERSION/mtg-${VERSION_MIN}-${sysName}-${ARCH}.tar.gz"
}

# download file
download_file() {
    url="${1}"
    destination="${2}"

    printf "Fetching ${url} \n\n"

    if test -x "$(command -v curl)"; then
        code=$(curl --connect-timeout 15 -w '%{http_code}' -L "${url}" -o "${destination}")
    elif test -x "$(command -v wget)"; then
        code=$(wget -t2 -T15 -O "${destination}" --server-response "${url}" 2>&1 | awk '/^  HTTP/{print $2}' | tail -1)
    else
        printf "\e[1;31mNeither curl nor wget was available to perform http requests.\e[0m\n"
        exit 1
    fi

    if [ "${code}" != 200 ]; then
        printf "\e[1;31mRequest failed with code %s\e[0m\n" $code
        exit 1
    else 
	    printf "\n\e[1;33mDownload succeeded\e[0m\n"
    fi
}

# /www/server/mtproxy/mtg/mtg run /www/server/mtproxy/mt.toml
Install_app()
{
	mkdir -p ${serverPath}/mtproxy
	mkdir -p ${serverPath}/source/mtproxy
	echo "${1}" > ${serverPath}/mtproxy/version.pl

	if [ "$OSNAME" == "centos" ]; then
    	yum install -y golang golang-src
	elif [ "$OSNAME" == "amazon" ]; then
	    yum install -y golang golang-src
	elif [ "$OSNAME" == "rocky" ]; then
	    yum install -y golang golang-src
	elif [ "$OSNAME" == "rhel" ]; then
	    yum install -y golang golang-src
	elif [ "$OSNAME" == "opensuse" ]; then
	    zypper install -y golang golang-src
	elif [ "$sysName" == "macos" ]; then
	    echo "macos"
	else
		apt install -y golang golang-src
	fi

	if [ "$sysName" == "darwin" ]; then
		ARCH=arm64
		DOWNLOAD_URL="https://github.com/9seconds/mtg/releases/download/$VERSION/mtg-${VERSION_MIN}-${sysName}-arm64.tar.gz"
	elif [ "$sysName" != "macos" ]; then
		get_arch
		get_download_url
	else
		echo "else"
	fi

	DOWNLOAD_FILE="$(mktemp).tar.gz"
	download_file $DOWNLOAD_URL $DOWNLOAD_FILE

	tar -C "$TARGET_DIR" -zxf $DOWNLOAD_FILE
	rm -rf $DOWNLOAD_FILE

	if [ -d ${serverPath}/mtproxy/mtg ];then
		rm -rf ${serverPath}/mtproxy/mtg
	fi

	# cd ${serverPath}/mtproxy
	# curl -s https://core.telegram.org/getProxySecret -o proxy-secret
	# curl -s https://core.telegram.org/getProxyConfig -o proxy-multi.conf
	

	mv ${serverPath}/mtproxy/mtg-${VERSION_MIN}-${sysName}-${ARCH} ${serverPath}/mtproxy/mtg
	echo '安装完成'

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/mtproxy/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/mtproxy/index.py initd_install
}

Uninstall_app()
{
	if [ -f /usr/lib/systemd/system/mtproxy.service ];then
		systemctl stop mtproxy
		rm -rf /usr/lib/systemd/system/mtproxy.service
		systemctl daemon-reload
	fi
	rm -rf ${serverPath}/mtproxy
	echo '卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app $2
else
	Uninstall_app $2
fi
