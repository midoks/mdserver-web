#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

version=$1
action=$2
extName=$3

echo $1,$2,$3

echo $curPath
echo $rootPath
echo $serverPath

# yum install -y php81-php-yar
if [ "$action" == 'install' ];then
	yum install -y php$1-php-$2
fi


# yum remove -y php81-php-yar
if [ "$action" == 'uninstall' ];then
	yum remove -y php$1-php-$2
fi


