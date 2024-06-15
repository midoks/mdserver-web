#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
export LANG=en_US.UTF-8
export DEBIAN_FRONTEND=noninteractive

if grep -Eq "Ubuntu" /etc/*-release; then
    sudo ln -sf /bin/bash /bin/sh
    #sudo dpkg-reconfigure dash
fi

apt update -y
apt autoremove -y

apt install -y wget curl lsof unzip
apt install -y rar unrar
apt install -y python3-pip
apt install -y python3-venv
apt install -y python3-dev
apt install -y expect
apt install -y pv
apt install -y bc
apt install -y cron
apt install -y net-tools
apt install -y libncurses5
apt install -y libncurses5-dev
apt install -y software-properties-common

apt install -y locate
locale-gen en_US.UTF-8
localedef -v -c -i en_US -f UTF-8 en_US.UTF-8

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
if [ "$SSH_PORT" == "" ];then
	SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep "Port \d*" | tail -1`
	SSH_PORT=${SSH_PORT_LINE/"Port "/""}
fi
echo "SSH PORT:${SSH_PORT}"

if [ -f /usr/sbin/ufw ];then
	# look
	# ufw status
	ufw enable

	if [ "$SSH_PORT" != "" ];then
		ufw allow $SSH_PORT/tcp
	else
		ufw allow 22/tcp
	fi

	ufw allow 80/tcp
	ufw allow 443/tcp
	ufw allow 443/udp
	# ufw allow 888/tcp
fi

if [ ! -f /usr/sbin/ufw ];then
	apt install -y firewalld
	systemctl enable firewalld
	

	if [ "$SSH_PORT" != "" ];then
		firewall-cmd --permanent --zone=public --add-port=${SSH_PORT}/tcp
	else
		firewall-cmd --permanent --zone=public --add-port=22/tcp
	fi

	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=443/udp
	# firewall-cmd --permanent --zone=public --add-port=888/tcp

	systemctl start firewalld

	# fix:debian10 firewalld faq
	# https://kawsing.gitbook.io/opensystem/andoid-shou-ji/untitled/fang-huo-qiang#debian-10-firewalld-0.6.3-error-commandfailed-usrsbinip6tablesrestorewn-failed-ip6tablesrestore-v1.8
	sed -i 's#IndividualCalls=no#IndividualCalls=yes#g' /etc/firewalld/firewalld.conf

	firewall-cmd --reload
	
	# #安装时不开启
	# systemctl stop firewalld
fi

apt install -y devscripts
apt install -y python3-dev
apt install -y autoconf
apt install -y gcc
apt install -y lrzsz

apt install -y libffi-dev
apt install -y cmake automake make

apt install -y webp scons
apt install -y libwebp-dev
apt install -y lzma lzma-dev
apt install -y libunwind-dev

apt install -y libpcre3 libpcre3-dev 
apt install -y openssl
apt install -y libssl-dev
apt install -y libargon2-dev

apt install -y libmemcached-dev
apt install -y libsasl2-dev
apt install -y imagemagick 
apt install -y libmagickwand-dev

apt install -y libxml2 libxml2-dev libbz2-dev libmcrypt-dev libpspell-dev librecode-dev
apt install -y libgmp-dev libgmp3-dev libreadline-dev libxpm-dev
apt install -y dia

apt install -y pkg-config
apt install -y zlib1g-dev

apt install -y libjpeg-dev libpng-dev
apt install -y libfreetype6
apt install -y libjpeg62-turbo-dev
apt install -y libfreetype6-dev
apt install -y libevent-dev libldap2-dev

apt install -y libzip-dev
apt install -y libicu-dev
apt install -y libyaml-dev 

# mqtt
apt install -y xsltproc

apt install -y build-essential

apt install -y libcurl4-openssl-dev
apt install -y libcurl4-nss-dev
apt install -y curl libcurl4-gnutls-dev
#https://blog.csdn.net/qq_36228377/article/details/123154344
# ln -s  /usr/include/x86_64-linux-gnu/curl  /usr/include/curl
if [ ! -d /usr/include/curl ];then
	SYS_ARCH=`arch`
	if [ -f /usr/include/x86_64-linux-gnu/curl ];then
		ln -s /usr/include/x86_64-linux-gnu/curl /usr/include/curl
	else
		# ln -s /usr/include/aarch64-linux-gnu/curl /usr/include/curl
		ln -s /usr/include/${SYS_ARCH}-linux-gnu/curl /usr/include/curl
	fi 
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

