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

# echo $1,$2,$3

# echo $curPath
# echo $rootPath
# echo $serverPath

FILE=${curPath}/${version}/${extName}.sh

# apt install -y php81-php-yar


if [ "$action" == 'install' ];then
	
	if [ -f $FILE ];then
		bash ${curPath}/${version}/${extName}.sh install
	else
		apt install -y php${version}-${extName}
	fi
fi


# apt remove -y php81-php-yar
if [ "$action" == 'uninstall' ];then

	if [ -f $FILE ];then
		bash ${curPath}/${version}/${extName}.sh uninstall
	else
		apt remove -y php${version}-${extName}
	fi
fi

echo "apt install -y php${version}-${extName}"
echo "apt remove -y php${version}-${extName}"



