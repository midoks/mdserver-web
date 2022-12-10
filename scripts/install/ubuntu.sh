#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export LANG=en_US.UTF-8
export DEBIAN_FRONTEND=noninteractive

if grep -Eq "Ubuntu" /etc/*-release; then
    sudo ln -sf /bin/bash /bin/sh
    #sudo dpkg-reconfigure dash
fi

apt update -y
apt-get update -y 

apt install -y wget curl lsof unzip
apt install -y python3-pip
apt install -y python3-venv
apt install -y python3-dev
apt install -y expect

apt install -y cron

apt install -y locate
locale-gen en_US.UTF-8
localedef -v -c -i en_US -f UTF-8 en_US.UTF-8


if [ -f /usr/sbin/ufw ];then

	ufw allow 22/tcp
	ufw allow 80/tcp
	ufw allow 443/tcp
	ufw allow 888/tcp
	# ufw allow 7200/tcp
	# ufw allow 3306/tcp
	# ufw allow 30000:40000/tcp

fi


if [ -f /usr/sbin/ufw ];then
	ufw disable
fi

if [ ! -f /usr/sbin/ufw ];then
	apt install -y firewalld
	systemctl enable firewalld
	systemctl start firewalld

	firewall-cmd --permanent --zone=public --add-port=22/tcp
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=888/tcp
	# firewall-cmd --permanent --zone=public --add-port=7200/tcp
	# firewall-cmd --permanent --zone=public --add-port=3306/tcp
	# firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp

	# fix:debian10 firewalld faq
	# https://kawsing.gitbook.io/opensystem/andoid-shou-ji/untitled/fang-huo-qiang#debian-10-firewalld-0.6.3-error-commandfailed-usrsbinip6tablesrestorewn-failed-ip6tablesrestore-v1.8
	sed -i 's#IndividualCalls=no#IndividualCalls=yes#g' /etc/firewalld/firewalld.conf

	firewall-cmd --reload
fi

#安装时不开启
systemctl stop firewalld


apt install -y devscripts
apt install -y net-tools
apt install -y python3-dev
apt install -y autoconf
apt install -y gcc

apt install -y libffi-dev
apt install -y cmake automake make

apt install -y webp scons
apt install -y libwebp-dev
apt install -y lzma lzma-dev
apt install -y libunwind-dev

apt install -y libpcre3 libpcre3-dev 
apt install -y openssl
apt install -y libssl-dev

apt install -y libmemcached-dev
apt install -y libsasl2-dev
apt install -y imagemagick 
apt install -y libmagickwand-dev

apt install -y libxml2 libxml2-dev libbz2-dev libmcrypt-dev libpspell-dev librecode-dev
apt install -y libgmp-dev libgmp3-dev libreadline-dev libxpm-dev
apt install -y dia pkg-config
apt install -y zlib1g-dev
apt install -y libjpeg-dev libpng-dev
apt install -y libfreetype6
apt install -y libjpeg62-turbo-dev
apt install -y libfreetype6-dev
apt install -y libevent-dev libncurses5-dev libldap2-dev
apt install -y libzip-dev
apt install -y libicu-dev

apt install -y build-essential

apt install -y libcurl4-openssl-dev
apt install -y curl libcurl4-gnutls-dev
#https://blog.csdn.net/qq_36228377/article/details/123154344
# ln -s  /usr/include/x86_64-linux-gnu/curl  /usr/include/curl
if [ ! -d /usr/include/curl ];then
    ln -s  /usr/include/x86_64-linux-gnu/curl  /usr/include/curl
fi


apt install -y graphviz bison re2c flex
apt install -y libsqlite3-dev
apt install -y libonig-dev

apt install -y perl g++ libtool    
apt install -y libxslt1-dev

apt install -y libmariadb-dev
#apt install -y libmysqlclient-dev   
apt install -y libmariadb-dev-compat
#apt install -y libmariadbclient-dev


# mysql8.0 在ubuntu22需要的库
apt install -y patchelf

VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
if [ "${VERSION_ID}" == "22.04" ];then
	apt install -y python3-cffi
    pip3 install -U --force-reinstall --no-binary :all: gevent
fi

cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data


if [ "${VERSION_ID}" == "22.04" ];then
	apt install -y python3-cffi
    pip3 install -U --force-reinstall --no-binary :all: gevent
fi

