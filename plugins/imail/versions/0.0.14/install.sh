#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=0.0.14


## cd /www/server/mdserver-web/plugins/imail && bash install.sh install 1.0

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

check_go_environment() {
	if test ! -x "$(command -v go)"; then
		printf "\e[1;31mmissing go running environment\e[0m\n"
		exit 1
	fi
}

get_arch() {
	echo "package main
import (
	\"fmt\"
	\"runtime\"
)
func main() { fmt.Println(runtime.GOARCH) }" > /tmp/go_arch.go

	ARCH=$(go run /tmp/go_arch.go)
}

load_vars() {
	OS=$(uname | tr '[:upper:]' '[:lower:]')
	TARGET_DIR="$serverPath/imail"
}

get_download_url() {
	DOWNLOAD_URL="https://github.com/midoks/imail/releases/download/$VERSION/imail_${VERSION}_${OS}_${ARCH}.tar.gz"
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


Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	check_go_environment
	load_vars
	get_arch
	get_download_url

	DOWNLOAD_FILE="$(mktemp).tar.gz"
	download_file $DOWNLOAD_URL $DOWNLOAD_FILE

	if [ ! -d "$TARGET_DIR" ]; then
		mkdir -p "$TARGET_DIR"
	fi

	tar -C "$TARGET_DIR" -zxf $DOWNLOAD_FILE
	rm -rf $DOWNLOAD_FILE

	pushd "$TARGET_DIR/scripts" >/dev/null 2>&1
	bash make.sh

	echo "$VERSION" > $serverPath/imail/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_App()
{
	rm -rf $serverPath/imail
	echo "Uninstall_Mail" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
