#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
export LANG=en_US.UTF-8
export DEBIAN_FRONTEND=noninteractive

VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")

ln -sf /bin/bash /bin/sh

__GET_BIT=`getconf LONG_BIT`
if [ "$__GET_BIT" == "32" ];then
	# install rust | 32bit need
	# curl https://sh.rustup.rs -sSf | sh
	apt install -y rustc
fi

if [ "$VERSION_ID" == "10" ];then
	apt install -y rustc
fi


# synchronize time first
apt-get install ntpdate -y
NTPHOST='time.nist.gov'
if [ ! -z "$cn" ];then
    NTPHOST='ntp1.aliyun.com'
fi
ntpdate $NTPHOST | logger -t NTP

apt install -y net-tools

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
if [ "$SSH_PORT" == "" ];then
	SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep "Port \d*" | tail -1`
	SSH_PORT=${SSH_PORT_LINE/"Port "/""}
fi
echo "SSH PORT:${SSH_PORT}"



# choose lang cmd
# dpkg-reconfigure --frontend=noninteractive locales
if [ ! -f /usr/sbin/locale-gen ];then
	apt install -y locales
	sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen
	locale-gen en_US.UTF-8
	localedef -v -c -i en_US -f UTF-8 en_US.UTF-8 > /dev/null 2>&1
	update-locale LANG=en_US.UTF-8
else
	locale-gen en_US.UTF-8
	localedef -v -c -i en_US -f UTF-8 en_US.UTF-8 > /dev/null 2>&1
fi

apt update -y
apt autoremove -y

apt install -y wget curl lsof unzip tar cron expect locate lrzsz
apt install -y rar 
apt install -y unrar
apt install -y pv
apt install -y bc
apt install -y python3-pip python3-dev python3-venv
apt install -y libncurses5
apt install -y libncurses5-dev

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
	# look
    # firewall-cmd --list-all
    # apt remove -y firewalld

	apt install -y firewalld
	systemctl enable firewalld
	#取消服务锁定
    systemctl unmask firewalld
	

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
fi

#fix zlib1g-dev fail
echo -e "\e[0;32mfix zlib1g-dev install question start\e[0m"
Install_TmpFile=/tmp/debian-fix-zlib1g-dev.txt
apt install -y zlib1g-dev > ${Install_TmpFile}
if [ "$?" != "0" ];then
	ZLIB1G_BASE_VER=$(cat ${Install_TmpFile} | grep zlib1g | awk -F "=" '{print $2}' | awk -F ")" '{print $1}')
	ZLIB1G_BASE_VER=`echo ${ZLIB1G_BASE_VER} | sed "s/^[ \s]\{1,\}//g;s/[ \s]\{1,\}$//g"`
	# echo "1${ZLIB1G_BASE_VER}1"
	echo -e "\e[1;31mapt install zlib1g=${ZLIB1G_BASE_VER} zlib1g-dev\e[0m"
	echo "Y" | apt install zlib1g=${ZLIB1G_BASE_VER}  zlib1g-dev
fi
rm -rf ${Install_TmpFile}
echo -e "\e[0;32mfix zlib1g-dev install question end\e[0m"


#fix libunwind-dev fail
echo -e "\e[0;32mfix libunwind-dev install question start\e[0m"
Install_TmpFile=/tmp/debian-fix-libunwind-dev.txt
apt install -y libunwind-dev > ${Install_TmpFile}
if [ "$?" != "0" ];then
	liblzma5_BASE_VER=$(cat ${Install_TmpFile} | grep liblzma-dev | awk -F "=" '{print $2}' | awk -F ")" '{print $1}')
	liblzma5_BASE_VER=`echo ${liblzma5_BASE_VER} | sed "s/^[ \s]\{1,\}//g;s/[ \s]\{1,\}$//g"`
	echo -e "\e[1;31mapt install liblzma5=${liblzma5_BASE_VER} libunwind-dev\e[0m"
	echo "Y" | apt install liblzma5=${liblzma5_BASE_VER} libunwind-dev
fi
rm -rf ${Install_TmpFile}
echo -e "\e[0;32mfix libunwind-dev install question end\e[0m"


apt install -y libvpx-dev
apt install -y libxpm-dev
apt install -y libwebp-dev
apt install -y libfreetype6
apt install -y libfreetype6-dev
apt install -y libjpeg-dev 
apt install -y libpng-dev

localedef -i en_US -f UTF-8 en_US.UTF-8

if [ "$VERSION_ID" == "9" ];then
	sed "s/flask==2.0.3/flask==1.1.1/g" -i /www/server/mdserver-web/requirements.txt
	sed "s/cryptography==3.3.2/cryptography==2.5/g" -i /www/server/mdserver-web/requirements.txt
	sed "s/configparser==5.2.0/configparser==4.0.2/g" -i /www/server/mdserver-web/requirements.txt
	sed "s/flask-socketio==5.2.0/flask-socketio==4.2.0/g" -i /www/server/mdserver-web/requirements.txt
	sed "s/python-engineio==4.3.2/python-engineio==3.9.0/g" -i /www/server/mdserver-web/requirements.txt
	# pip3 install -r /www/server/mdserver-web/requirements.txt
fi

apt install -y build-essential
apt install -y devscripts

apt install -y autoconf
apt install -y gcc
apt install -y patchelf

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

apt install -y libevent-dev libldap2-dev
apt install -y libzip-dev
apt install -y libicu-dev
apt install -y libyaml-dev 

apt install -y xsltproc

apt install -y libcurl4-openssl-dev
apt install -y curl libcurl4-gnutls-dev

# Disabled due to dependency issues
#apt install --ignore-missing -y autoconf automake cmake curl dia gcc imagemagick libbz2-dev libcurl4-gnutls-dev\
#    libcurl4-openssl-dev libevent-dev libffi-dev libfreetype6 libfreetype6-dev libgmp-dev libgmp3-dev libicu-dev \
#	libjpeg-dev libldap2-dev libmagickwand-dev libmcrypt-dev libmemcached-dev libncurses5-dev \
#	libpcre3 libpcre3-dev libpng-dev libpspell-dev libreadline-dev librecode-dev libsasl2-dev libssl-dev \
#	libunwind-dev libwebp-dev libxml2 libxml2-dev libxpm-dev libzip-dev lzma lzma-dev make net-tools openssl \
#	pkg-config python3-dev scons webp zlib1g-dev

if [ "$VERSION_ID" != "9" ]; then
	apt install -y libjpeg62-turbo-dev
fi

#https://blog.csdn.net/qq_36228377/article/details/123154344
# ln -s  /usr/include/x86_64-linux-gnu/curl  /usr/include/curl
if [ ! -d /usr/include/curl ];then
	SYS_ARCH=`arch`
	if [ -f /usr/include/x86_64-linux-gnu/curl ];then
		ln -s /usr/include/x86_64-linux-gnu/curl /usr/include/curl
	else
		ln -s /usr/include/${SYS_ARCH}-linux-gnu/curl /usr/include/curl
	fi 
fi

apt install -y graphviz bison re2c flex libsqlite3-dev libonig-dev perl g++ libtool libxslt1-dev
apt install -y libmariadb-dev libmariadb-dev-compat

#apt install -y libmysqlclient-dev
#apt install -y libmariadbclient-dev


cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data