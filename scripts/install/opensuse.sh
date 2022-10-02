#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

# zypper refresh


# systemctl stop SuSEfirewall2

# for debug
zypper install -y htop
# for debug end

zypper install -y openssl openssl-devel
zypper install -y bison re2c make cmake gcc
zypper install -y gcc-c++
zypper install -y autoconf
zypper install -y python3-pip
zypper install -y pcre pcre-devel
zypper install -y graphviz libxml2 libxml2-devel
zypper install -y curl curl-devel
zypper install -y freetype freetype-devel
zypper install -y mysql-devel
zypper install -y ImageMagick ImageMagick-devel
zypper install -y libjpeg-devel libpng-devel
zypper install -y libevent-devel
zypper install -y libtirpc-devel
zypper install -y rpcgen
zypper install -y expect

zypper install -y libzip libzip-devel
zypper install -y libmemcached libmemcached-devel

zypper install -y icu libicu-devel
zypper install -y sqlite3 sqlite3-devel
zypper install -y oniguruma-devel

# zypper install -y libmcrypt libmcrypt-devel
# zypper install -y protobuf
# zypper install -y zlib-devel

zypper install -y python3-devel
zypper install -y python-devel

zypper install -y libwebp-devel
zypper install -y libtomcrypt
zypper install -y libtomcrypt-devel

zypper install -y libXpm-devel
zypper install -y freetype2-devel

# zypper install -y  php-config
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
	zypper install -y firewalld 
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

