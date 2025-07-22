#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
LANG=en_US.UTF-8

# apk refresh


# systemctl stop SuSEfirewall2

# for debug
apk add htop
# for debug end

apk add openssl openssl-devel
apk add bison re2c make cmake gcc
apk add gcc-c++
apk add autoconf
apk add python3-pip
apk add pcre pcre-devel
apk add graphviz libxml2 libxml2-devel
apk add curl curl-devel
apk add freetype freetype-devel
apk add mysql-devel
apk add ImageMagick ImageMagick-devel
apk add libjpeg-devel libpng-devel
apk add libevent-devel
apk add libtirpc-devel
apk add rpcgen
apk add libstdc++6
apk add expect
apk add pv
apk add bc
apk add bzip2

apk add libzip libzip-devel
apk add unrar rar
apk add libmemcached libmemcached-devel

apk add icu libicu-devel
apk add sqlite3 sqlite3-devel
apk add oniguruma-devel

# apk add libmcrypt libmcrypt-devel
# apk add protobuf
# apk add zlib-devel

apk add python3-devel
apk add python-devel

apk add libwebp-devel
apk add libtomcrypt
apk add libtomcrypt-devel

apk add libXpm-devel
apk add freetype2-devel
apk add libargon2-devel

apk add net-tools-deprecated
apk add numactl

# apk add  php-config

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
if [ "$SSH_PORT" == "" ];then
	SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep "Port \d*" | tail -1`
	SSH_PORT=${SSH_PORT_LINE/"Port "/""}
fi
echo "SSH PORT:${SSH_PORT}"

if [ ! -f /usr/sbin/firewalld ];then
	apk add firewalld 
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

