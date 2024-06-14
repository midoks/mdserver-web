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
FILE_COMMON=${curPath}/common/${extName}.sh
# yum install -y php81-php-yar
# yum install -y php74-php-pecl-mysql


if [ "$action" == 'install' ];then
	
	if [ -f $FILE ];then
		bash ${curPath}/${version}/${extName}.sh install
	elif [ -f $FILE_COMMON ];then
		bash ${FILE_COMMON} install ${version}
	else
		yum install -y php${version}-php-${extName}
	fi

	# if [ "${extName}" == "mysql" ];then
	# 	yum install -y php74-php-pecl-mysql
	# fi
fi

# yum remove -y php81-php-yar
if [ "$action" == 'uninstall' ];then

	if [ -f $FILE ];then
		bash ${curPath}/${version}/${extName}.sh uninstall
	elif [ -f $FILE_COMMON ];then
		bash ${FILE_COMMON} uninstall ${version}
	else
		yum remove -y php${version}-php-${extName}
	fi
fi

echo "yum install -y php${version}-php-${extName}"
echo "yum remove -y php${version}-php-${extName}"


echo "systemctl restart php${version}-php-fpm"
php_status=`systemctl status php${version}-php-fpm | grep inactive`
echo "php_status:${php_status}"
if [ "$php_status" == "" ];then
	systemctl restart php${version}-php-fpm
fi



