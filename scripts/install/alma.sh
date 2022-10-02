#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=C.UTF-8



setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

dnf install -y wget lsof
dnf install -y python3-devel
dnf install -y python-devel
dnf install -y crontabs
dnf install -y mysql-devel

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
	yum install firewalld -y
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
fi


#安装时不开启
systemctl stop firewalld

dnf upgrade -y
dnf autoremove -y

dnf groupinstall -y "Development Tools"
dnf install -y epel-release
dnf install -y zip unzip

dnf install -y libevent libevent-devel  libmcrypt libmcrypt-devel
dnf install -y wget libicu-devel  bzip2-devel gcc libxml2 libxml2-devel libjpeg-devel libpng-devel libwebp libwebp-devel pcre pcre-devel
dnf install -y lsof net-tools
dnf install -y ncurses-devel cmake

dnf --enablerepo=crb install -y mysql-devel
dnf --enablerepo=crb install -y oniguruma oniguruma-devel
dnf --enablerepo=crb install -y rpcgen
dnf --enablerepo=crb install -y libzip-devel
dnf --enablerepo=crb install -y libmemcached-devel
dnf --enablerepo=crb install -y libtirpc libtirpc-devel
dnf --enablerepo=crb install -y patchelf

dnf install -y langpacks-zh_CN langpacks-en langpacks-en_GB


yum install -y libtirpc libtirpc-devel
yum install -y rpcgen
yum install -y openldap openldap-devel  
yum install -y bison re2c cmake
yum install -y cmake3
yum install -y autoconf
yum install -y expect

yum install -y curl curl-devel
yum install -y zlib zlib-devel
yum install -y libzip libzip-devel
yum install -y pcre pcre-devel
yum install -y icu libicu-devel 
yum install -y freetype freetype-devel
yum install -y openssl openssl-devel
yum install -y graphviz libxml2 libxml2-devel
yum install -y sqlite-devel
yum install -y oniguruma oniguruma-devel
yum install -y ImageMagick ImageMagick-devel


for yumPack in make cmake gcc gcc-c++ flex bison file libtool libtool-libs autoconf kernel-devel patch wget gd gd-devel libxml2 libxml2-devel zlib zlib-devel glib2 glib2-devel tar bzip2 bzip2-devel libevent libevent-devel ncurses ncurses-devel curl curl-devel libcurl libcurl-devel e2fsprogs e2fsprogs-devel libidn libidn-devel vim-minimal gettext gettext-devel ncurses-devel gmp-devel libcap diffutils ca-certificates net-tools psmisc libXpm-devel git-core c-ares-devel libicu-devel libxslt libxslt-devel zip unzip glibc.i686 libstdc++.so.6 cairo-devel bison-devel ncurses-devel libaio-devel perl perl-devel perl-Data-Dumper lsof crontabs expat-devel readline-devel;
do dnf --enablerepo=crb install -y $yumPack;done


# findLD=`cat /etc/ld.so.conf | grep '/usr/local/lib64'`
# echo "/usr/local/lib64" >> /etc/ld.so.conf


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


