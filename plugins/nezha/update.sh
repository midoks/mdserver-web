#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /www/server/mdserver-web && bash plugins/nezha/update.sh

curPath=`pwd`
echo $curPath

REPO="nezhahq/nezha"
LATEST_VERSION=$(curl -sL "https://api.github.com/repos/$REPO/releases/latest" | jq -r '.tag_name')
echo "最新版本是: $LATEST_VERSION"
NUMBER_LATEST_VERSION=${LATEST_VERSION:1}
echo "最新[NUMBER]是: $NUMBER_LATEST_VERSION"

INSTALL_VERSION=`cat /www/server/nezha/version.pl`
echo "安装的版本: $INSTALL_VERSION"


echo "ok"