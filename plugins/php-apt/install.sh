#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

if id www &> /dev/null ;then 
    echo "www UID is `id -u www`"
    echo "www Shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	# useradd -g www -s /sbin/nologin www
	useradd -g www -s /bin/bash www
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

if [ "${2}" == "" ];then
	echo '缺少安装脚本...' > $install_tmp
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本2...' > $install_tmp
	exit 0
fi



if [ "$OSNAME" == "ubuntu" ];then
	echo "y" | LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php && apt update -y
fi
# apt install $(grep-aptavail -S PHP-defaults -s Package -n)

if [ ! -f /etc/apt/sources.list.d/php.list ] && [ "$OSNAME" == "debian" ];then
# install php source

apt update -y
apt -y install apt-transport-https lsb-release ca-certificates curl
curl -sSLo /usr/share/keyrings/deb.sury.org-php.gpg https://packages.sury.org/php/apt.gpg
sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list'
apt update -y

fi 


if [ "${action}" == "uninstall" ] && [ -d ${serverPath}/php-apt/${type} ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py stop ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py initd_uninstall ${type}
fi

cd ${curPath} && sh -x $curPath/versions/$2/install.sh $1

if [ "${action}" == "install" ] && [ -d ${serverPath}/php-apt/${type} ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py restart ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/php-apt/index.py initd_install ${type}
fi


