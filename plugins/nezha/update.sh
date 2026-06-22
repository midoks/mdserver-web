#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /www/server/mdserver-web && bash plugins/nezha/update.sh
curPath=`pwd`
serverPath=$(dirname "$curPath")
echo $curPath

nezhaDir=${serverPath}/source/nezha

REPO="nezhahq/nezha"
LATEST_VERSION=$(curl -sL "https://api.github.com/repos/$REPO/releases/latest" | jq -r '.tag_name')
echo "最新版本是: $LATEST_VERSION"
NUMBER_LATEST_VERSION=${LATEST_VERSION:1}
echo "最新[NUMBER]是: $NUMBER_LATEST_VERSION"

INSTALL_VERSION=`cat /www/server/nezha/version.pl`
echo "安装的版本: $INSTALL_VERSION"

if [ "$INSTALL_VERSION" == "$NUMBER_LATEST_VERSION" ];then
	echo "已经是最新!!!"
	exit
fi

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
get_arch

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

TARGET_DIR="$serverPath/nezha/dashboard"
filename="dashboard-linux-${ARCH}.zip"
DOWNLOAD_URL="https://github.com/nezhahq/nezha/releases/download/v${NUMBER_LATEST_VERSION}/${filename}"


DOWNLOAD_FILE="$nezhaDir/$filename"
if [ ! -f $DOWNLOAD_FILE ];then
	download_file $DOWNLOAD_URL $DOWNLOAD_FILE
fi

if [ ! -d $TARGET_DIR ]; then
	mkdir -p $TARGET_DIR
fi

unzip $DOWNLOAD_FILE -d $TARGET_DIR
echo "TARGET_DIR:"$TARGET_DIR

cd $TARGET_DIR && rm -rf app
cd $TARGET_DIR && rm -rf dashboard-linux-${ARCH}
if [ ! -f $TARGET_DIR/app ];then
	cd $TARGET_DIR && mv dashboard-linux-${ARCH} app && chmod +x app
fi

echo $DOWNLOAD_URL

rm -rf $DOWNLOAD_FILE
echo "ok"