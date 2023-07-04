#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=0.15.2

# bash install.sh install 0.15.2
# cd /www/server/mdserver-web/plugins/nezha && bash install.sh install 0.15.2
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/nezha && bash install.sh install 0.15.2

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

load_vars() {
	OS=$(uname | tr '[:upper:]' '[:lower:]')
	TARGET_DIR="$serverPath/nezha/dashboard"


	    ## China_IP
    if [[ -z "${CN}" ]]; then
        if [[ $(curl -m 10 -s https://ipapi.co/json | grep 'China') != "" ]]; then
            CN=true
        fi
    fi
    
    if [[ -z "${CN}" ]]; then
        GITHUB_RAW_URL="raw.githubusercontent.com/midoks/nezha/main"
        GITHUB_URL="github.com"
    else
        GITHUB_RAW_URL="cdn.jsdelivr.net/gh/midoks/nezha@main"
        GITHUB_URL="dn-dao-github-mirror.daocloud.io"
    fi

    echo $GITHUB_RAW_URL
    echo $GITHUB_URL
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


Install_dashborad(){
	echo '正在安装哪吒监控...' > $install_tmp
	mkdir -p $serverPath/source

	if [ ! -f $TARGET_DIR/nezha ];then

		DOWNLOAD_URL="https://${GITHUB_URL}/midoks/nezha/releases/download/v${VERSION}/nezha-${OS}-${ARCH}.zip"

		DOWNLOAD_FILE="$(mktemp).zip"
		download_file $DOWNLOAD_URL $DOWNLOAD_FILE

		if [ ! -d $TARGET_DIR ]; then
			mkdir -p $TARGET_DIR
		fi

		unzip $DOWNLOAD_FILE -d $TARGET_DIR
		rm -rf $DOWNLOAD_FILE
	fi

}

Install_agent(){
	echo -e "正在下载监控端" > $install_tmp
	mkdir -p $serverPath/source

	version=v0.15.1

	AGENT_TARGET_DIR="$serverPath/nezha/agent"

	DOWNLOAD_URL="https://${GITHUB_URL}/nezhahq/agent/releases/download/${version}/nezha-agent_${OS}_${ARCH}.zip"
	DOWNLOAD_FILE="$(mktemp).zip"

	if [ ! -f $AGENT_TARGET_DIR/nezha-agent ];then
		download_file $DOWNLOAD_URL $DOWNLOAD_FILE

		if [ ! -d $AGENT_TARGET_DIR ]; then
			mkdir -p $AGENT_TARGET_DIR
		fi
	
		unzip $DOWNLOAD_FILE -d $AGENT_TARGET_DIR
		rm -rf $DOWNLOAD_FILE
	fi
}

Install_App()
{
	load_vars
	get_arch

	Install_dashborad
	Install_agent

	if [ -d $serverPath/nezha ];then
		echo "$VERSION" > $serverPath/nezha/version.pl
		cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py init_cfg
	fi
	echo 'install successful' > $install_tmp
}

Uninstall_App()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py initd_uninstall
	cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py initd_uninstall_agent
	cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py stop
	cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py stop_agent
	rm -rf $serverPath/nezha
	echo "install fail" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
