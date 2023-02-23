#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export LANG=en_US.UTF-8

if [ ! -f /usr/bin/applydeltarpm ];then
    yum -y provides '*/applydeltarpm'
    yum -y install deltarpm
fi

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
fi

#https need
if [ ! -d /root/.acme.sh ];then
    curl https://get.acme.sh | sh
fi

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
echo "SSH PORT:${SSH_PORT}"

# redhat , iptables no default
# echo "iptables wrap start"
# if [ -f /usr/sbin/iptables ];then
#     $PKGMGR install -y iptables-services

#     # iptables -nL --line-number
    
#     echo "iptables start"
#     iptables_status=`systemctl status iptables | grep 'inactive'`
#     if [ "${iptables_status}" != '' ];then
#         service iptables restart
        
#         # iptables -P FORWARD DROP
#         iptables -P INPUT DROP
#         iptables -P OUTPUT ACCEPT
#         iptables -A INPUT -p tcp -s 127.0.0.1 -j ACCEPT
        
#         if [ "$SSH_PORT" != "" ];then
#             iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport ${SSH_PORT} -j ACCEPT
#         else
#             iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
#         fi

#         iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
#         iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
#         iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 888 -j ACCEPT
#         # iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 7200 -j ACCEPT
#         # iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 3306 -j ACCEPT
#         # iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 30000:40000 -j ACCEPT
#         service iptables save
#     fi
    
#     # 安装时不开启
#     # stop之后清空了所有规则,所以安装是不能stop.
#     # 要在代码修复这个问题，开启时，重新执行一下放行端口。
#     #service iptables stop

#     echo "iptables end"
# fi
# echo "iptables wrap start"

if [ ! -f /usr/sbin/firewalld ];then
    $PKGMGR install firewalld -y
    systemctl enable firewalld
    #取消服务锁定
    systemctl unmask firewalld
    systemctl start firewalld

    sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
    firewall-cmd --reload
    
    # look
    # firewall-cmd --list-all

    if [ "$SSH_PORT" != "" ];then
        firewall-cmd --permanent --zone=public --add-port=${SSH_PORT}/tcp
    else
        firewall-cmd --permanent --zone=public --add-port=22/tcp
    fi
    firewall-cmd --permanent --zone=public --add-port=80/tcp
    firewall-cmd --permanent --zone=public --add-port=443/tcp
    firewall-cmd --permanent --zone=public --add-port=888/tcp
    # firewall-cmd --permanent --zone=public --add-port=7200/tcp
    # firewall-cmd --permanent --zone=public --add-port=3306/tcp
    # firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp

    # sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
    firewall-cmd --reload

    #安装时不开启
    systemctl stop firewalld
fi

$PKGMGR install -y epel-release
if [ ! -z "$cn" ];then
    sed -e 's|^metalink=|#metalink=|g' \
        -e 's|^#baseurl=|baseurl=|g' \
        -e 's|//download\.fedoraproject\.org/pub|//mirrors.tuna.tsinghua.edu.cn|g' \
        -e 's|//download\.example/pub|//mirrors.tuna.tsinghua.edu.cn|g' \
        -i.bak /etc/yum.repos.d/epel*.repo
fi
$PKGMGR makecache
$PKGMGR groupinstall -y "Development Tools"

if [ $VERSION_ID -ge 8 ];then
    # EL8 及以上
    if [ $VERSION_ID -ge 9 ];then
        REPOS='--enablerepo=appstream,baseos,epel,extras,crb'
    else
        REPOS='--enablerepo=appstream,baseos,epel,extras,powertools'
    fi

    for rpms in autoconf bzip2 bzip2-devel c-ares-devel \
        ca-certificates cairo-devel cmake crontabs curl curl-devel diffutils e2fsprogs e2fsprogs-devel \
        expat-devel expect file flex gcc gcc-c++ gd gd-devel gettext gettext-devel glib2 glib2-devel glibc.i686 \
        gmp-devel kernel-devel libXpm-devel libaio-devel libcap libcurl libcurl-devel libevent libevent-devel \
        libicu-devel libidn libidn-devel libmcrypt libmcrypt-devel libmemcached libmemcached-devel \
        libpng libpng-devel libstdc++.so.6 libtirpc libtirpc-devel libtool libtool-libs libwebp libwebp-devel \
        libxml2 libxml2-devel libxslt libxslt-devel libarchive lsof make mysql-devel ncurses ncurses-devel net-tools \
        oniguruma oniguruma-devel patch pcre pcre-devel perl perl-Data-Dumper perl-devel procps psmisc python3-devel \
        readline-devel rpcgen sqlite-devel tar unzip vim-minimal wget zip zlib zlib-devel ;
    do
        dnf $REPOS install -y $rpms;
        if [ "$?" != "0" ];then
            dnf install -y $rpms;
        fi
    done
else
    # CentOS 7
    for rpms in autoconf bison bzip2 bzip2-devel c-ares-devel ca-certificates cairo-devel \
        cmake cmake3 crontabs curl curl-devel diffutils e2fsprogs e2fsprogs-devel expat-devel expect file \
        flex freetype freetype-devel gcc gcc-c++ gd gd-devel gettext gettext-devel git-core glib2 glib2-devel \
        glibc.i686 gmp-devel graphviz icu kernel-devel libXpm-devel libaio-devel libcap libcurl libcurl-devel \
        libevent libevent-devel libicu-devel libidn libidn-devel libjpeg-devel libmcrypt libmcrypt-devel \
        libmemcached libmemcached-devel libpng-devel libstdc++.so.6 libtirpc libtirpc-devel libtool libtool-libs \
        libwebp libwebp-devel libxml2 libxml2-devel libxslt libxslt-devel libzip libzip-devel libzstd-devel lsof \
        make mysql-devel ncurses ncurses-devel net-tools oniguruma oniguruma-devel openldap openldap-devel \
        openssl openssl-devel patch pcre pcre-devel perl perl-Data-Dumper perl-devel psmisc python-devel \
        python3-devel python3-pip re2c readline-devel rpcgen sqlite-devel tar unzip vim-minimal vixie-cron \
        wget zip zlib zlib-devel ImageMagick ImageMagick-devel ;
    do
        yum install -y $rpms;
    done
fi

cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data
