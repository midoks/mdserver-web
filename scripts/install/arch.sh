#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
LANG=en_US.UTF-8



echo y | pacman -Sy yaourt

echo y | pacman -Sy gcc make cmake autoconf
echo y | pacman -Sy pkg-config
echo y | pacman -Sy unrar
echo y | pacman -Sy rar
echo y | pacman -Sy python3
echo y | pacman -Sy lsof
echo y | pacman -Sy python-pip
echo y | pacman -Sy curl
echo y | pacman -Sy libevent

echo y | pacman -Sy libzip
echo y | pacman -Sy libxml2
echo y | pacman -Sy libtirpc

echo y | pacman -Sy cronie
echo y | pacman -Sy vi
echo y | pacman -Sy openssl
echo y | pacman -Sy pcre
echo y | pacman -Sy libmcrypt
echo y | pacman -Sy oniguruma
echo y | pacman -Sy libmemcached
echo y | pacman -Sy bison re2c 
echo y | pacman -Sy graphviz
echo y | pacman -Sy mhash
echo y | pacman -Sy ncurses
echo y | pacman -Sy sqlite
echo y | pacman -Sy libtool
echo y | pacman -Sy imagemagick
echo y | pacman -Sy mariadb-clients
echo y | pacman -Sy rpcsvc-proto
echo y | pacman -Sy lemon
echo y | pacman -Sy which
echo y | pacman -Sy expect

## gd start
echo y | pacman -Sy gd
# echo y | pacman -Sy libgd
echo y | pacman -Sy libjpeg
echo y | pacman -Sy libpng
echo y | pacman -Sy libvpx
echo y | pacman -Sy libwebp
echo y | pacman -Sy libxpm
echo y | pacman -Syu freetype2
## gd end

echo y | pacman -Syu icu

hwclock --systohc

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
if [ "$SSH_PORT" == "" ];then
	SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep "Port \d*" | tail -1`
	SSH_PORT=${SSH_PORT_LINE/"Port "/""}
fi
echo "SSH PORT:${SSH_PORT}"

# if [ -f /usr/sbin/iptables ];then

# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 888 -j ACCEPT
# 	service iptables save

# 	iptables_status=`service iptables status | grep 'not running'`
# 	if [ "${iptables_status}" == '' ];then
# 		service iptables restart
# 	fi

# 	#安装时不开启
# 	service iptables stop
# fi


if [ ! -f /usr/sbin/firewalld ];then
	echo y | pacman -Sy firewalld
	systemctl enable firewalld
	systemctl start firewalld

	if [ "$SSH_PORT" != "" ];then
		firewall-cmd --permanent --zone=public --add-port=${SSH_PORT}/tcp
	else
		firewall-cmd --permanent --zone=public --add-port=22/tcp
	fi
	
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	# firewall-cmd --permanent --zone=public --add-port=888/tcp

	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	firewall-cmd --reload
	#安装时不开启
	systemctl stop firewalld
fi


cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data
