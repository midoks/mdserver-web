#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
LANG=en_US.UTF-8


if [ ! -f /usr/bin/applydeltarpm ];then
	yum -y provides '*/applydeltarpm'
	yum -y install deltarpm
fi


setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

yum install -y wget lsof
yum install -y unrar rar
yum install -y python3-devel
yum install -y crontabs
yum install -y expect
yum install -y curl curl-devel libcurl libcurl-devel

if [ -f /usr/sbin/iptables ];then

	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
	# iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 888 -j ACCEPT
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


if [ ! -f /usr/sbin/iptables ];then
	yum install firewalld -y
	systemctl enable firewalld
	systemctl start firewalld

	firewall-cmd --permanent --zone=public --add-port=22/tcp
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	# firewall-cmd --permanent --zone=public --add-port=888/tcp
	# firewall-cmd --permanent --zone=public --add-port=7200/tcp
	# firewall-cmd --permanent --zone=public --add-port=3306/tcp
	# firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp


	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	firewall-cmd --reload
fi


#安装时不开启
systemctl stop firewalld

yum groupinstall -y "Development Tools"
yum install -y epel-release

yum install -y libevent libevent-devel zip unzip libmcrypt libmcrypt-devel
yum install -y wget libicu-devel readline-devel zip bzip2 bzip2-devel libxml2 libxml2-devel
yum install -y libpng libpng-devel libwebp libwebp-devel pcre pcre-devel gd gd-devel zlib zlib-devel gettext gettext-devel
yum install -y net-tools
yum install -y ncurses ncurses-devel mysql-devel make cmake
yum install -y sqlite-devel
yum install -y libargon2-dev

# python-imaging
# yum install -y MySQL-python


yum install -y perl perl-devel perl-Data-Dumper

for yumPack in  gcc gcc-c++ flex file libtool libtool-libs autoconf kernel-devel patch glib2 glib2-devel tar e2fsprogs e2fsprogs-devel libidn libidn-devel vim-minimal gmp-devel libcap diffutils ca-certificates libc-client-devel psmisc libXpm-devel c-ares-devel libxslt libxslt-devel glibc.i686 libstdc++.so.6 cairo-devel libaio-devel expat-devel;
do dnf --enablerepo=powertools install -y $yumPack;done

yum install -y libtirpc libtirpc-devel
dnf --enablerepo=powertools install -y boost-locale

dnf --enablerepo=powertools install -y libmemcached libmemcached-devel
dnf --enablerepo=powertools install -y rpcgen
dnf --enablerepo=powertools install -y oniguruma oniguruma-devel
dnf --enablerepo=powertools install -y re2c bison bison-devel
dnf install -y libjpeg-turbo libjpeg-turbo-devel

cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data

echo "rocky ok"
