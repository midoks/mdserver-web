#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8



echo y | pacman -Sy yaourt

echo y | pacman -Sy gcc make cmake autoconf
echo y | pacman -Sy pkg-config
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

#https need
if [ ! -d /root/.acme.sh ];then	
	curl https://get.acme.sh | sh
fi

if [ -f /etc/init.d/iptables ];then

	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 888 -j ACCEPT
	# iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 7200 -j ACCEPT
	# iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 3306 -j ACCEPT
	# iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 30000:40000 -j ACCEPT
	service iptables save

	iptables_status=`service iptables status | grep 'not running'`
	if [ "${iptables_status}" == '' ];then
		service iptables restart
	fi

	#安装时不开启
	service iptables stop
fi


if [ ! -f /etc/init.d/iptables ];then
	echo y | pacman -Sy firewalld
	systemctl enable firewalld
	systemctl start firewalld

	firewall-cmd --permanent --zone=public --add-port=22/tcp
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=888/tcp
	# firewall-cmd --permanent --zone=public --add-port=7200/tcp
	# firewall-cmd --permanent --zone=public --add-port=3306/tcp
	# firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp


	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	firewall-cmd --reload
	#安装时不开启
	systemctl stop firewalld
fi


cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data


cd /www/server/mdserver-web && ./cli.sh start
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
n=0
while [[ ! -f /etc/init.d/mw ]];
do
    echo -e ".\c"
    sleep 1
    let n+=1
    if [ $n -gt 20 ];then
    	echo -e "start mw fail"
        exit 1
    fi
done

cd /www/server/mdserver-web && /etc/init.d/mw stop
cd /www/server/mdserver-web && /etc/init.d/mw start
cd /www/server/mdserver-web && /etc/init.d/mw default