#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

VERSION=2.2.6

# bash install.sh install 2.2.6
# cd /www/server/mdserver-web/plugins/nezha && bash install.sh install 2.2.6
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/nezha && bash install.sh install 2.2.6

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


ARCH="amd64"

geo_check() {
    api_list="https://blog.cloudflare.com/cdn-cgi/trace https://developers.cloudflare.com/cdn-cgi/trace"
    ua="Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"
    set -- "$api_list"
    for url in $api_list; do
        text="$(curl -A "$ua" -m 10 -s "$url")"
        endpoint="$(echo "$text" | sed -n 's/.*h=\([^ ]*\).*/\1/p')"
        if echo "$text" | grep -qw 'CN'; then
            isCN=true
            break
        elif echo "$url" | grep -q "$endpoint"; then
            break
        fi
    done
}

get_arch() {
    uname=$(uname -m)
    case "$uname" in
        amd64|x86_64)
            ARCH="amd64"
            ;;
        i386|i686)
            ARCH="386"
            ;;
        aarch64|arm64)
            ARCH="arm64"
            ;;
        *arm*)
            ARCH="arm"
            ;;
        s390x)
            ARCH="s390x"
            ;;
        riscv64)
            ARCH="riscv64"
            ;;
        *)
            err "未知架构：$ARCH"
            exit 1
            ;;
    esac
}

load_vars() {
	OS=$(uname | tr '[:upper:]' '[:lower:]')
	TARGET_DIR="$serverPath/nezha/dashboard"

	# China_IP
    # if [[ -z "${CN}" ]]; then
    #     if [[ $(curl -m 10 -s https://ipapi.co/json | grep 'China') != "" ]]; then
    #         CN=true
    #     fi
    # fi
    
    GITHUB_RAW_URL="raw.githubusercontent.com/nezhahq/nezha/main"
    GITHUB_URL="github.com"
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
	echo '正在安装哪吒监控...'
	mkdir -p $serverPath/source

	if [ ! -f $TARGET_DIR/nezha ];then

		DOWNLOAD_URL="https://${GITHUB_URL}/nezhahq/nezha/releases/download/v${VERSION}/dashboard-${OS}-${ARCH}.zip"

		DOWNLOAD_FILE="$(mktemp).zip"
		download_file $DOWNLOAD_URL $DOWNLOAD_FILE

		if [ ! -d $TARGET_DIR ]; then
			mkdir -p $TARGET_DIR
		fi

		unzip $DOWNLOAD_FILE -d $TARGET_DIR
		rm -rf $DOWNLOAD_FILE
	fi

}

Install_App()
{
	load_vars
	get_arch

	Install_dashborad

	if [ -d $serverPath/nezha ];then
		echo "$VERSION" > $serverPath/nezha/version.pl
		cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py init_cfg
	fi
	echo 'install successful'
}

Uninstall_App()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py initd_uninstall
	cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py stop
	cd ${rootPath} && python3 ${rootPath}/plugins/nezha/index.py stop_agent
	rm -rf $serverPath/nezha
	echo "install fail"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
