#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=C.UTF-8

setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

VERSION_ID=`grep -o -i 'release *[[:digit:]]\+\.*' /etc/redhat-release | grep -o '[[:digit:]]\+' `
isStream=$(grep -o -i 'stream' /etc/redhat-release)

cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")

# CentOS Stream
if [ ! -z "$stream" ];then
    yum install -y dnf dnf-plugins-core
    dnf upgrade -y libmodulemd
fi

PKGMGR='yum'

if [ $VERSION_ID -ge 8 ];then
    PKGMGR='dnf'
    if [ ! -z "$cn" ];then
    	dnf install -y http://mirrors.cloud.tencent.com/epel/epel-release-latest-$VERSION_ID.noarch.rpm
    else
    	dnf install -y epel-release
    fi
    if [ $VERSION_ID -ge 9 ];then
        REPOS='--enablerepo=appstream,baseos,epel,extras,crb'
    else
        REPOS='--enablerepo=appstream,baseos,epel,extras,powertools'
    fi
    dnf $REPOS makecache
    dnf groupinstall -y "Development Tools"
    dnf $REPOS install -y --allowerasing --skip-broken autoconf bzip2 bzip2-devel c-ares-devel \
        ca-certificates cairo-devel cmake crontabs curl curl-devel diffutils e2fsprogs e2fsprogs-devel \
        expat-devel expect file flex gcc gcc-c++ gd gd-devel gettext gettext-devel glib2 glib2-devel glibc.i686 \
        gmp-devel kernel-devel libXpm-devel libaio-devel libcap libcurl libcurl-devel libevent libevent-devel \
        libicu-devel libidn libidn-devel libmcrypt libmcrypt-devel libmemcached libmemcached-devel \
        libpng libpng-devel libstdc++.so.6 libtirpc libtirpc-devel libtool libtool-libs libwebp libwebp-devel \
        libxml2 libxml2-devel libxslt libxslt-devel lsof make mysql-devel ncurses ncurses-devel net-tools \
        oniguruma oniguruma-devel patch pcre pcre-devel perl perl-Data-Dumper perl-devel procps psmisc python3-devel \
        readline-devel rpcgen sqlite-devel tar unzip vim-minimal wget zip zlib zlib-devel
else
    # CentOS 7
    yum makecache
    yum groupinstall -y "Development Tools"
    yum install -y --skip-broken autoconf bison bzip2 bzip2-devel c-ares-devel ca-certificates cairo-devel \
        cmake cmake3 crontabs curl curl-devel diffutils e2fsprogs e2fsprogs-devel expat-devel expect file \
        flex freetype freetype-devel gcc gcc-c++ gd gd-devel gettext gettext-devel git-core glib2 glib2-devel \
        glibc.i686 gmp-devel graphviz icu kernel-devel libXpm-devel libaio-devel libcap libcurl libcurl-devel \
        libevent libevent-devel libicu-devel libidn libidn-devel libjpeg-devel libmcrypt libmcrypt-devel \
        libmemcached libmemcached-devel libpng-devel libstdc++.so.6 libtirpc libtirpc-devel libtool libtool-libs \
        libwebp libwebp-devel libxml2 libxml2-devel libxslt libxslt-devel libzip libzip-devel libzstd-devel lsof \
        make mysql-devel ncurses ncurses-devel net-tools oniguruma oniguruma-devel openldap openldap-devel \
        openssl openssl-devel patch pcre pcre-devel perl perl-Data-Dumper perl-devel psmisc python-devel \
        python3-devel python3-pip re2c readline-devel rpcgen sqlite-devel tar unzip vim-minimal vixie-cron \
        wget zip zlib zlib-devel ImageMagick ImageMagick-devel
fi

#https need
if [ ! -d /root/.acme.sh ];then	
	curl https://get.acme.sh | sh
fi

if [ -f /usr/sbin/iptables ];then
	$PKGMGR install -y iptables-services
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

if [ ! -f /usr/sbin/iptables ];then
	$PKGMGR install firewalld -y
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
