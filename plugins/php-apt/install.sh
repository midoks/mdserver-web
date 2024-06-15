#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

if id www &> /dev/null ;then 
    echo "www uid is `id -u www`"
    echo "www shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	useradd -g www -s /sbin/nologin www
	# useradd -g www -s /bin/bash www
fi

_os=`uname`
if [ ${_os} == "Darwin" ]; then
    OSNAME='macos'
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
    OSNAME='debian'
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
    OSNAME='ubuntu'
else
    OSNAME='unknow'
fi

action=$1
type=$2
apt_ver=${type:0:1}.${type:1:2}

if [ "${2}" == "" ];then
	echo '缺少安装脚本...' > $install_tmp
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...' > $install_tmp
	exit 0
fi



if [ "$OSNAME" == "ubuntu" ];then
	find_source=`ls /etc/apt/sources.list.d | grep ondrej-ubuntu-php`
	if [ "$find_source" == "" ];then
		echo "y" | LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php && apt update -y
	fi
fi
# apt install $(grep-aptavail -S PHP-defaults -s Package -n)


if [ ! -f /etc/apt/sources.list.d/php.list ] && [ "$OSNAME" == "debian" ];then
	# install php source
	apt install -y apt-transport-https lsb-release ca-certificates curl
	cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
	if [ ! -z "$cn" ];then
		curl -sSLo /usr/share/keyrings/deb.sury.org-php.gpg https://mirror.sjtu.edu.cn/sury/php/apt.gpg
	 	sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://mirror.sjtu.edu.cn/sury/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list'
	else
	 	curl -sSLo /usr/share/keyrings/deb.sury.org-php.gpg https://packages.sury.org/php/apt.gpg
		sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list'
	fi
	apt update -y
fi 


if [ "${action}" == "uninstall" ] && [ -d ${serverPath}/php-apt/${type} ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py stop ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py initd_uninstall ${type}

	if [ -f /lib/systemd/system/php${apt_ver}-fpm.service ];then
		rm -rf /lib/systemd/system/php${apt_ver}-fpm.service
	fi

	if [ -f /lib/systemd/system/system/php${apt_ver}-fpm.service ];then
		rm -rf /lib/systemd/system/php${apt_ver}-fpm.service
	fi

	systemctl daemon-reload
fi

cd ${curPath} && sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d ${serverPath}/php-apt/${type} ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py restart ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py initd_install ${type}

	# 安装通用扩展
	echo "install PHP-APT[${type}] extend start"
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install curl
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install gd
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install iconv
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install exif
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install intl
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install xml
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install mcrypt
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install mysqlnd
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install mysql
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install gettext
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install redis
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install memcached
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install mbstring
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install zip
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install mongodb
	cd ${rootPath}/plugins/php-apt/versions && bash common.sh ${apt_ver} install opcache
	echo "install PHP-APT[${type}] extend end"

	if [ ! -f /usr/local/bin/composer ];then
		cd /tmp
		curl -sS https://getcomposer.org/installer | /usr/bin/php${apt_ver}
		mv composer.phar /usr/local/bin/composer
	fi

	systemctl restart php${apt_ver}-fpm
fi


