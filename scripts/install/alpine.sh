#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
LANG=en_US.UTF-8


# for debug
apk add htop --force-broken-world
apk add linux-headers --force-broken-world
# for debug end
apk add shadow --force-broken-world
apk add build-base --force-broken-world
apk add openssl openssl-devel --force-broken-world
apk add bison re2c make cmake gcc --force-broken-world
apk add gcc-c++ --force-broken-world
apk add autoconf --force-broken-world
apk add python3-pip --force-broken-world
apk add pcre pcre-devel --force-broken-world
apk add graphviz libxml2 libxml2-devel --force-broken-world
apk add curl curl-devel --force-broken-world
apk add freetype freetype-devel --force-broken-world
apk add mysql-devel --force-broken-world
apk add ImageMagick ImageMagick-devel --force-broken-world
apk add libjpeg-devel libpng-devel --force-broken-world
apk add libevent-devel --force-broken-world
apk add libtirpc-devel --force-broken-world
apk add rpcgen --force-broken-world
apk add libstdc++6 --force-broken-world
apk add expect --force-broken-world
apk add pv --force-broken-world
apk add bc --force-broken-world
apk add bzip2 --force-broken-world

apk add libzip libzip-devel --force-broken-world
apk add unrar rar --force-broken-world
apk add libmemcached libmemcached-devel --force-broken-world

apk add icu libicu-devel --force-broken-world
apk add sqlite3 sqlite3-devel --force-broken-world
apk add oniguruma-devel --force-broken-world

# apk add libmcrypt libmcrypt-devel
# apk add protobuf
# apk add zlib-devel

apk add python3-devel --force-broken-world
apk add python-devel --force-broken-world

apk add libwebp-devel --force-broken-world
apk add libtomcrypt --force-broken-world
apk add libtomcrypt-devel --force-broken-world

apk add libXpm-devel --force-broken-world
apk add freetype2-devel --force-broken-world
apk add libargon2-devel --force-broken-world

apk add net-tools-deprecated --force-broken-world
apk add numactl --force-broken-world

# apk add  php-config

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
if [ "$SSH_PORT" == "" ];then
	SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep "Port \d*" | tail -1`
	SSH_PORT=${SSH_PORT_LINE/"Port "/""}
fi
echo "SSH PORT:${SSH_PORT}"

if [ ! -f /usr/sbin/firewalld ];then
	apk add firewalld --force-broken-world
	which systemctl && systemctl enable firewalld
	which systemctl && systemctl start firewalld

	if [ "$SSH_PORT" != "" ];then
		which firewall-cmd && firewall-cmd --permanent --zone=public --add-port=${SSH_PORT}/tcp
	else
		which firewall-cmd && firewall-cmd --permanent --zone=public --add-port=22/tcp
	fi
	
	which firewall-cmd && firewall-cmd --permanent --zone=public --add-port=80/tcp
	which firewall-cmd && firewall-cmd --permanent --zone=public --add-port=443/tcp
	which firewall-cmd && firewall-cmd --permanent --zone=public --add-port=443/udp
	# firewall-cmd --permanent --zone=public --add-port=888/tcp

	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	which systemctl && firewall-cmd --reload
	#安装时不开启
	which systemctl && systemctl stop firewalld
fi

cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data

