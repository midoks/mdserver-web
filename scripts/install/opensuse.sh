#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
LANG=en_US.UTF-8

# zypper refresh


# systemctl stop SuSEfirewall2

# for debug
zypper install -y htop
# for debug end

zypper install -y openssl
zypper install -y openssl-devel
zypper install -y libopenssl-devel

zypper install -y bison
zypper install -y flex
zypper install -y re2c
zypper install -y make
zypper install -y cmake
zypper install -y gcc
zypper install -y gcc-c++
zypper install -y autoconf

zypper install -y python3-pip
zypper install -y pcre pcre-devel
zypper install -y graphviz libxml2 libxml2-devel
zypper install -y curl
zypper install -y curl-devel
zypper install -y freetype freetype-devel
zypper install -y mysql-devel
zypper install -y ImageMagick ImageMagick-devel
zypper install -y libjpeg-devel libpng-devel
zypper install -y libevent-devel
zypper install -y libtirpc-devel
zypper install -y rpcgen
zypper install -y libstdc++6
zypper install -y expect
zypper install -y pv
zypper install -y bc
zypper install -y bzip2


zypper install -y libzip
zypper install -y libzip-devel
zypper install -y rar
zypper install -y unrar
zypper install -y libmemcached
zypper install -y libmemcached-devel

zypper install -y icu libicu-devel
zypper install -y sqlite3 sqlite3-devel
zypper install -y oniguruma-devel
zypper install -y libzstd-devel
zypper install -y libudev-devel

# zypper install -y libmcrypt libmcrypt-devel
# zypper install -y protobuf
zypper install -y zlib-devel
zypper install -y readline-devel

zypper install -y python3-devel
zypper install -y python-devel

zypper install -y libwebp-devel
zypper install -y libtomcrypt
zypper install -y libtomcrypt-devel

zypper install -y libXpm-devel
zypper install -y freetype2-devel
zypper install -y libargon2-devel

zypper install -y net-tools-deprecated
zypper install -y numactl
zypper install -y sshpass
zypper install -y brotli-devel
zypper install -y git

zypper install -y libcurl-devel
zypper install -y libxml2-devel
zypper install -y libxslt-devel
zypper install -y perl
zypper install -y perl-devel
# zypper install -y  php-config

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
if [ "$SSH_PORT" = "" ];then
	SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep "Port \d*" | tail -1`
	SSH_PORT=${SSH_PORT_LINE/"Port "/""}
fi
echo "SSH PORT:${SSH_PORT}"

if [ ! -f /usr/sbin/firewalld ];then
	zypper install -y firewalld 
	systemctl enable firewalld
	systemctl start firewalld

	if [ "$SSH_PORT" != "" ];then
		firewall-cmd --permanent --zone=public --add-port=${SSH_PORT}/tcp
	else
		firewall-cmd --permanent --zone=public --add-port=22/tcp
	fi
	
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=443/udp
	# firewall-cmd --permanent --zone=public --add-port=888/tcp

	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	firewall-cmd --reload
	#安装时不开启
	systemctl stop firewalld
fi

cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data

