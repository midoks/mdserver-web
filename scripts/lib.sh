#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
public_file=/www/server/panel/install/public.sh
if [ ! -f $public_file ];then
	wget -O $public_file http://download.bt.cn/install/public.sh -T 5;
fi
. $public_file
download_Url=$NODE_URL
mkdir -p /www/server
run_path="/root"
Is_64bit=`getconf LONG_BIT`

centos_version=`cat /etc/redhat-release | grep ' 7.' | grep -i centos`
if [ "${centos_version}" != '' ]; then
	rpm_path="centos7"
else
	rpm_path="centos6"
fi

Install_SendMail()
{
	yum install postfix mysql-libs -y
	if [ "${centos_version}" != '' ];then
		systemctl start postfix
		systemctl enable postfix	
	else
		service postfix start
		chkconfig --level 2345 postfix on
	fi
}

Install_Curl()
{
	if [ -f "/usr/local/curl/newcurl.pl" ];then
		return;
	fi
	cd ${run_path}
	curl_version="7.54.1"
	if [ ! -f "curl-$curl_version.tar.gz" ];then
		wget -O curl-$curl_version.tar.gz ${download_Url}/src/curl-$curl_version.tar.gz -T 5
	fi
	tar zxf curl-$curl_version.tar.gz
	cd curl-$curl_version
    ./configure --prefix=/usr/local/curl --enable-ares --without-nss --with-ssl=/usr/local/openssl
    make && make install
    cd ..
    rm -rf curl-$curl_version
	rm -rf curl-$curl_version.tar.gz
	echo -e "Install_Curl" >> /www/server/lib.pl
	echo -e "Ture" >> /usr/local/curl/newcurl.pl
}

Install_Libiconv()
{
	if [ -d '/usr/local/libiconv' ];then
		return
	fi
	cd ${run_path}
	if [ ! -f "libiconv-1.14.tar.gz" ];then
		wget -O libiconv-1.14.tar.gz ${download_Url}/src/libiconv-1.14.tar.gz -T 5
	fi
	mkdir /patch
	wget -O /patch/libiconv-glibc-2.16.patch ${download_Url}/src/patch/libiconv-glibc-2.16.patch -T 5
	tar zxf libiconv-1.14.tar.gz
	cd libiconv-1.14
    patch -p0 < /patch/libiconv-glibc-2.16.patch
    ./configure --prefix=/usr/local/libiconv --enable-static
    make && make install
    cd ${run_path}
    rm -rf libiconv-1.14
	rm -f libiconv-1.14.tar.gz
	echo -e "Install_Libiconv" >> /www/server/lib.pl
}

Install_Libmcrypt()
{
	if [ -f '/usr/local/lib/libmcrypt.so' ];then
		return;
	fi
	cd ${run_path}
	if [ ! -f "libmcrypt-2.5.8.tar.gz" ];then
		wget -O libmcrypt-2.5.8.tar.gz ${download_Url}/src/libmcrypt-2.5.8.tar.gz -T 5
	fi
	tar zxf libmcrypt-2.5.8.tar.gz
	cd libmcrypt-2.5.8
	
    ./configure
    make && make install
    /sbin/ldconfig
    cd libltdl/
    ./configure --enable-ltdl-install
    make && make install
    ln -sf /usr/local/lib/libmcrypt.la /usr/lib/libmcrypt.la
    ln -sf /usr/local/lib/libmcrypt.so /usr/lib/libmcrypt.so
    ln -sf /usr/local/lib/libmcrypt.so.4 /usr/lib/libmcrypt.so.4
    ln -sf /usr/local/lib/libmcrypt.so.4.4.8 /usr/lib/libmcrypt.so.4.4.8
    ldconfig
    cd ${run_path}
    rm -rf libmcrypt-2.5.8
	rm -f libmcrypt-2.5.8.tar.gz
	echo -e "Install_Libmcrypt" >> /www/server/lib.pl
}

Install_Mcrypt()
{
	if [ -f '/usr/bin/mcrypt' ] || [ -f '/usr/local/bin/mcrypt' ];then
		return;
	fi
	cd ${run_path}
	if [ ! -f "mcrypt-2.6.8.tar.gz" ];then
		wget -O mcrypt-2.6.8.tar.gz ${download_Url}/src/mcrypt-2.6.8.tar.gz -T 5
	fi
	tar zxf mcrypt-2.6.8.tar.gz
	cd mcrypt-2.6.8
    ./configure
    make && make install
    cd ${run_path}
    rm -rf mcrypt-2.6.8
	rm -f mcrypt-2.6.8.tar.gz
	echo -e "Install_Mcrypt" >> /www/server/lib.pl
}

Install_Mhash()
{
	if [ -f '/usr/local/lib/libmhash.so' ];then
		return;
	fi
	cd ${run_path}
	if [ ! -f "mhash-0.9.9.9.tar.gz" ];then
		wget -O mhash-0.9.9.9.tar.gz ${download_Url}/src/mhash-0.9.9.9.tar.gz -T 5
	fi
	tar zxf mhash-0.9.9.9.tar.gz
	cd mhash-0.9.9.9
    ./configure
    make && make install
    ln -sf /usr/local/lib/libmhash.a /usr/lib/libmhash.a
    ln -sf /usr/local/lib/libmhash.la /usr/lib/libmhash.la
    ln -sf /usr/local/lib/libmhash.so /usr/lib/libmhash.so
    ln -sf /usr/local/lib/libmhash.so.2 /usr/lib/libmhash.so.2
    ln -sf /usr/local/lib/libmhash.so.2.0.1 /usr/lib/libmhash.so.2.0.1
    ldconfig
    cd ${run_path}
    rm -rf mhash-0.9.9.9*
	echo -e "Install_Mhash" >> /www/server/lib.pl
}


Install_Freetype()
{
	if [ -d /usr/local/freetype ];then
		return;
	fi
	cd ${run_path}
	if [ ! -f "freetype-2.4.12.tar.gz" ];then
		wget -O freetype-2.4.12.tar.gz ${download_Url}/src/freetype-2.4.12.tar.gz -T 5
	fi
	tar zxf freetype-2.4.12.tar.gz
	cd freetype-2.4.12
    ./configure --prefix=/usr/local/freetype
    make && make install

    cat > /etc/ld.so.conf.d/freetype.conf<<EOF
/usr/local/freetype/lib
EOF
    ldconfig
    ln -sf /usr/local/freetype/include/freetype2 /usr/local/include
    ln -sf /usr/local/freetype/include/ft2build.h /usr/local/include
    cd ${run_path}
    rm -rf freetype-2.4.12
	rm -f freetype-2.4.12.tar.gz
	echo -e "Install_Freetype" >> /www/server/lib.pl
}

Install_Pcre()
{
    Cur_Pcre_Ver=`pcre-config --version|grep '^8.' 2>&1`
    if [ "$Cur_Pcre_Ver" == "" ];then
		pcre_version=8.40
        wget -O pcre-$pcre_version.tar.gz ${download_Url}/src/pcre-$pcre_version.tar.gz -T 5
		tar zxf pcre-$pcre_version.tar.gz
		cd pcre-$pcre_version
		if [ "$Is_64bit" == "64" ];then
			./configure --prefix=/usr --docdir=/usr/share/doc/pcre-$pcre_version --libdir=/usr/lib64 --enable-unicode-properties --enable-pcre16 --enable-pcre32 --enable-pcregrep-libz --enable-pcregrep-libbz2 --enable-pcretest-libreadline --disable-static --enable-utf8  
        else
			./configure --prefix=/usr --docdir=/usr/share/doc/pcre-$pcre_version --enable-unicode-properties --enable-pcre16 --enable-pcre32 --enable-pcregrep-libz --enable-pcregrep-libbz2 --enable-pcretest-libreadline --disable-static --enable-utf8
		fi
		make && make install
        cd ..
        rm -rf pcre-$pcre_version
		rm -f pcre-$pcre_version.tar.gz
    fi
}

Install_OpenSSL()
{
    if [ ! -d "/usr/local/openssl" ];then
        cd ${run_path}
        wget ${download_Url}/src/openssl-1.0.2l.tar.gz -T 20
        tar -zxf openssl-1.0.2l.tar.gz
        rm -f openssl-1.0.2l.tar.gz
        cd openssl-1.0.2l
        ./config --openssldir=/usr/local/openssl zlib-dynamic shared
        make && make install
        echo '1.0.2l_shared' > /usr/local/openssl/version.pl
        cd ..
        rm -rf openssl-1.0.2l
		cat > /etc/ld.so.conf.d/openssl.conf <<EOF
/usr/local/openssl/lib
EOF
ldconfig
    fi
}
Install_Lib()
{
if [ -f "/www/server/nginx/sbin/nginx" ] || [ -f "/www/server/apache/bin/httpd" ] || [ -f "/www/server/mysql/bin/mysql" ]; then
	return
fi
lockFile='/www/server/panel/data/bt_lib.lock'
if [ ! -f "${lockFile}" ];then
	sed -i "s#SELINUX=enforcing#SELINUX=disabled#" /etc/selinux/config
	rpm -e --nodeps mariadb-libs-*
	
	mv /etc/yum.repos.d/epel.repo /etc/yum.repos.d/epel.repo.backup
	rm -f /var/run/yum.pid
	for yumPack in make cmake gcc gcc-c++ gcc-g77 flex bison file libtool libtool-libs autoconf kernel-devel patch wget libjpeg libjpeg-devel libpng libpng-devel libpng10 libpng10-devel gd gd-devel libxml2 libxml2-devel zlib zlib-devel glib2 glib2-devel tar bzip2 bzip2-devel libevent libevent-devel ncurses ncurses-devel curl curl-devel libcurl libcurl-devel e2fsprogs e2fsprogs-devel krb5 krb5-devel libidn libidn-devel openssl openssl-devel vim-minimal gettext gettext-devel ncurses-devel gmp-devel pspell-devel libcap diffutils ca-certificates net-tools libc-client-devel psmisc libXpm-devel git-core c-ares-devel libicu-devel libxslt libxslt-devel zip unzip glibc.i686 libstdc++.so.6 cairo-devel bison-devel ncurses-devel libaio-devel perl perl-devel perl-Data-Dumper lsof pcre pcre-devel vixie-cron crontabs expat-devel readline-devel;
	do yum -y install $yumPack;done
	
	Install_SendMail
	mv /etc/yum.repos.d/epel.repo.backup /etc/yum.repos.d/epel.repo
	groupadd www
	useradd -s /sbin/nologin -M -g www www
	echo 'true' > $lockFile
fi
}

Install_Lib
Install_OpenSSL
Install_Pcre
Install_Curl
Install_Mhash
Install_Libmcrypt
Install_Mcrypt	
Install_Libiconv