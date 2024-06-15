#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
install_tmp=${rootPath}/tmp/mw_install.pl

if id www &> /dev/null ;then 
    echo "www uid is `id -u www`"
    echo "www shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	useradd -g www -s /sbin/nologin www
	# useradd -g www -s /bin/bash www
fi

action=$1
type=$2

if [ "${2}" == "" ];then
	echo '缺少安装脚本...' > $install_tmp
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...' > $install_tmp
	exit 0
fi


# if [ "${action}" == "install" ] && [ -d $serverPath/php/${type} ];then
# 	exit 0
# fi

if [ "${action}" == "uninstall" ];then
	
	if [ -f /usr/lib/systemd/system/php${type}.service ] || [ -f /lib/systemd/system/php${type}.service ] ;then
		systemctl stop php${type}
		systemctl disable php${type}
		rm -rf /usr/lib/systemd/system/php${type}.service
		rm -rf /lib/systemd/system/php${type}.service
		systemctl daemon-reload
	fi
fi

cd ${curPath} && sh -x $curPath/versions/$2/install.sh $1


if [ "${action}" == "install" ] && [ -d ${serverPath}/php/${type} ];then

	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php/index.py initd_install ${type}

	# 安装通用扩展
	echo "install PHP${type} extend start"

	# cd /www/server/mdserver-web/plugins/php/versions/common  && bash iconv.sh install 53
	# cd /www/server/mdserver-web/plugins/php/versions/common  && bash intl.sh install 73
	# cd /www/server/mdserver-web/plugins/php/versions/common  && bash gd.sh install 56
	# cd /www/server/mdserver-web/plugins/php/versions/common  && bash openssl.sh install 56
	# cd /www/server/mdserver-web/plugins/php/versions/common  && bash fileinfo.sh install 81
	cd ${rootPath}/plugins/php/versions/common && bash gd.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash iconv.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash exif.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash intl.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash mcrypt.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash openssl.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash bcmath.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash gettext.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash redis.sh install ${type}
	cd ${rootPath}/plugins/php/versions/common && bash memcached.sh install ${type}

	if [ "${type}" -gt "73" ];then
		cd ${rootPath}/plugins/php/versions/common && bash zlib.sh install ${type}
	fi

	echo "install PHP${type} extend end"

	if [ ! -f /usr/local/bin/composer ] && [ "$sysName" != "Darwin" ] ;then
		cd /tmp
		curl -sS https://getcomposer.org/installer | /www/server/php/${type}/bin/php
		mv composer.phar /usr/local/bin/composer
	fi
fi


