#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
serverPath=$(dirname "$rootPath")
sourcePath=$serverPath/source/lib
libPath=$serverPath/lib

mkdir -p $sourcePath
mkdir -p $libPath
rm -rf ${libPath}/lib.pl

Install_Zlib()
{
#----------------------------- zlib start -------------------------#
if [ ! -d ${libPath}/zlib ];then
    cd ${sourcePath}
    if [ ! -f ${sourcePath}/zlib-1.2.11.tar.gz ];then
    	wget -O zlib-1.2.11.tar.gz https://github.com/madler/zlib/archive/v1.2.11.tar.gz -T 20
    fi 
    tar -zxf zlib-1.2.11.tar.gz
    cd zlib-1.2.11
    ./configure --prefix=${libPath}/zlib && make && make install
fi
echo -e "Install_Zlib" >> ${libPath}/lib.pl
#----------------------------- zlib end  -------------------------#
}


Install_Libzip()
{
#----------------------------- libzip start -------------------------#
if [ ! -d ${libPath}/libzip ];then
    cd ${sourcePath}
    if [ ! -f ${sourcePath}/libzip-1.3.2.tar.gz ];then
    	wget -O libzip-1.3.2.tar.gz --no-check-certificate https://nih.at/libzip/libzip-1.3.2.tar.gz -T 20
    fi 
    tar -zxf libzip-1.3.2.tar.gz
    cd libzip-1.3.2
    ./configure --prefix=${libPath}/libzip && make && make install
fi
echo -e "Install_Libzip" >> ${libPath}/lib.pl
#----------------------------- libzip end  -------------------------#
}


Install_Libmemcached()
{
#----------------------------- libmemcached start -------------------------#
if [ ! -d ${libPath}/libmemcached ];then
    cd ${sourcePath}
    if [ ! -f ${sourcePath}/libmemcached-1.0.4.tar.gz ];then
    	wget -O libmemcached-1.0.4.tar.gz https://launchpad.net/libmemcached/1.0/1.0.4/+download/libmemcached-1.0.4.tar.gz -T 20
    fi 
    tar -zxf libmemcached-1.0.4.tar.gz
    cd libmemcached-1.0.4
    ./configure --prefix=${libPath}/libmemcached -with-memcached && make && make install
fi
echo -e "Install_Libmemcached" >> ${libPath}/lib.pl
#----------------------------- libmemcached end -------------------------#
}


Install_Libiconv()
{
#----------------------------- libiconv start -------------------------#
cd ${sourcePath}
if [ ! -d ${libPath}/libiconv ];then
	# wget -O libiconv-1.15.tar.gz  https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.15.tar.gz  -T 5
	wget -O libiconv-1.15.tar.gz  https://github.com/midoks/mdserver-web/releases/download/init/libiconv-1.15.tar.gz  -T 5
	tar zxvf libiconv-1.15.tar.gz
	cd libiconv-1.15
    ./configure --prefix=${libPath}/libiconv --enable-static
    make && make install
    cd ${sourcePath}
    rm -rf libiconv-1.15
	rm -rf libiconv-1.15.tar.gz
fi
echo -e "Install_Libiconv" >> ${libPath}/lib.pl
#----------------------------- libiconv end -------------------------#
}

Install_Freetype()
{
#----------------------------- freetype start -------------------------#
cd ${sourcePath}
if [ ! -d ${libPath}/freetype_old ];then
    wget -O freetype-2.7.1.tar.gz --no-check-certificate https://download.savannah.gnu.org/releases/freetype/freetype-2.7.1.tar.gz  -T 5
    tar zxvf freetype-2.7.1.tar.gz
    cd freetype-2.7.1
    ./configure --prefix=${libPath}/freetype_old
    make && make install
    cd ${sourcePath}
    rm -rf freetype-2.7.1.tar.gz
    rm -rf freetype-2.7.1
fi
echo -e "Install_Freetype_Old" >> ${libPath}/lib.pl
#----------------------------- freetype end -------------------------#
}

Install_Freetype_New()
{
#----------------------------- freetype start -------------------------#
cd ${sourcePath}
if [ ! -d ${libPath}/freetype ];then
    wget -O freetype-2.12.1.tar.gz --no-check-certificate https://download.savannah.gnu.org/releases/freetype/freetype-2.12.1.tar.gz  -T 5
    tar zxvf freetype-2.12.1.tar.gz
    cd freetype-2.12.1
    ./configure --prefix=${libPath}/freetype
    make && make install
    cd ${sourcePath}
    rm -rf freetype-2.12.1.tar.gz
    rm -f freetype-2.12.1.tar.gz
fi
echo -e "Install_Freetype" >> ${libPath}/lib.pl
#----------------------------- freetype end -------------------------#
}

Install_Libmcrypt()
{
#----------------------------- libmcrypt start -------------------------#
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
#----------------------------- libmcrypt start -------------------------#
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
    if [ ! -d ${libPath}/openssl ];then
        cd ${sourcePath}
        if [ ! -f ${sourcePath}/openssl-1.0.2q.tar.gz ];then
        	wget https://github.com/midoks/mdserver-web/releases/download/init/openssl-1.0.2q.tar.gz -T 20
        fi 
        tar -zxf openssl-1.0.2q.tar.gz
        cd openssl-1.0.2q
        ./config --openssldir=${libPath}/openssl zlib-dynamic shared
        make && make install
    fi
    echo -e "Install_OpenSSL" >> ${libPath}/lib.pl
}

Install_Lib()
{
	if [ -f "/www/server/nginx/sbin/nginx" ] || [ -f "/www/server/apache/bin/httpd" ] || [ -f "/www/server/mysql/bin/mysql" ]; then
		return
	fi
	lockFile='${libPath}/data/mw_lib.lock'
	if [ ! -f "${lockFile}" ];then
		sed -i "s#SELINUX=enforcing#SELINUX=disabled#" /etc/selinux/config
		rpm -e --nodeps mariadb-libs-*
		
		mv /etc/yum.repos.d/epel.repo /etc/yum.repos.d/epel.repo.backup
		rm -f /var/run/yum.pid
		for yumPack in make cmake gcc gcc-c++ gcc-g77 flex bison file libtool libtool-libs autoconf kernel-devel patch wget libjpeg libjpeg-devel libpng libpng-devel libpng10 libpng10-devel gd gd-devel libxml2 libxml2-devel zlib zlib-devel glib2 glib2-devel tar bzip2 bzip2-devel libevent libevent-devel ncurses ncurses-devel curl curl-devel libcurl libcurl-devel e2fsprogs e2fsprogs-devel krb5 krb5-devel libidn libidn-devel openssl openssl-devel vim-minimal gettext gettext-devel ncurses-devel gmp-devel pspell-devel libcap diffutils ca-certificates net-tools libc-client-devel psmisc libXpm-devel git-core c-ares-devel libicu-devel libxslt libxslt-devel zip unzip glibc.i686 libstdc++.so.6 cairo-devel bison-devel ncurses-devel libaio-devel perl perl-devel perl-Data-Dumper lsof pcre pcre-devel vixie-cron crontabs expat-devel readline-devel;
		do yum -y install $yumPack;done
		
		mv /etc/yum.repos.d/epel.repo.backup /etc/yum.repos.d/epel.repo
		groupadd www
		useradd -s /sbin/nologin -M -g www www
		echo 'true' > $lockFile
	fi
}


Install_Curl()
{
#----------------------------- curl start -------------------------#

if [ ! -d ${libPath}/curl ];then
    cd ${sourcePath}
    if [ ! -f ${sourcePath}/curl-7.64.0.tar.gz ];then
    	wget https://curl.haxx.se/download/curl-7.64.0.tar.gz -T 20
    fi 
    tar -zxf curl-7.64.0.tar.gz
    cd curl-7.64.0
    ./configure --prefix=${libPath}/curl --with-ssl=${libPath}/openssl
    make && make install
fi
echo -e "Install_Curl" >> ${libPath}/lib.pl
#----------------------------- curl end -------------------------#
}


_os=`uname`

if grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
    sudo ln -sf /bin/bash /bin/sh
    #sudo dpkg-reconfigure dash
fi

if [ ${_os} == "Darwin" ]; then
    OSNAME='macos'
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
    OSNAME='centos'
elif grep -Eqi "Red Hat Enterprise Linux Server" /etc/issue || grep -Eq "Red Hat Enterprise Linux Server" /etc/*-release; then
    OSNAME='rhel'
elif grep -Eqi "Aliyun" /etc/issue || grep -Eq "Aliyun" /etc/*-release; then
    OSNAME='aliyun'
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
    OSNAME='fedora'
elif grep -Eqi "Amazon Linux AMI" /etc/issue || grep -Eq "Amazon Linux AMI" /etc/*-release; then
    OSNAME='amazon'
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
    OSNAME='debian'
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
    OSNAME='ubuntu'
elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
    OSNAME='raspbian'
elif grep -Eqi "Deepin" /etc/issue || grep -Eq "Deepin" /etc/*-release; then
    OSNAME='deepin'
else
    OSNAME='unknow'
fi


# system judge
if [ "$OSNAME" == "macos" ]; then
    brew install libmemcached
    brew install curl
    brew install zlib
    brew install freetype
    brew install openssl
    brew install libzip

elif [ "$OSNAME" == "ubuntu"  ] || [ "$OSNAME" == "debian" ]; then
    
    apt install -y devscripts

    apt install -y libffi-dev
    apt install -y cmake automake make

    apt install -y php-common webp scons
    apt install -y lzma lzma-dev libunwind-dev

    apt install -y libpcre3 libpcre3-dev 
    apt install -y openssl

    apt install -y libxml2 libxml2-dev libbz2-dev libmcrypt-dev libpspell-dev librecode-dev
    apt install -y libgmp-dev libgmp3-dev libreadline-dev libxpm-dev
    apt install -y zlib1g-dev dia pkg-config  
    apt install -y libjpeg62-turbo-dev libjpeg-dev libpng-dev
    apt install -y libfreetype6
    apt install -y libfreetype6-dev
    apt install -y libevent-dev libncurses5-dev libldap2-dev

    apt install -y libicu-dev

    apt install -y gcc build-essential libssl-dev 
    
    apt install -y curl libcurl4-gnutls-dev
    #https://blog.csdn.net/qq_36228377/article/details/123154344
    ln -s  /usr/include/x86_64-linux-gnu/curl  /usr/include/curl

    apt install -y graphviz bison re2c flex
    apt install -y libsqlite3-dev
    apt install -y libonig-dev

    apt install -y perl g++ libtool    
    apt install -y libxslt1-dev

    apt install -y libmariadb-dev
    #apt install -y libmysqlclient-dev   
    apt install -y libmariadb-dev-compat
    #apt install -y libmariadbclient-dev 
else

    yum install -y openldap openldap-devel libtirpc libtirpc-devel rpcgen

    yum install -y bison re2c cmake

    yum install -y libmemcached libmemcached-devel
    yum install -y curl-devel
    yum install -y zlib zlib-devel
    yum install -y pcre pcre-devel
    yum install -y icu libicu-devel autoconf
    yum install -y freetype freetype-devel
    yum install -y openssl openssl-devel
    yum install -y libzip libzip-devel
    yum install -y graphviz libxml2 libxml2-devel

    yum install -y sqlite-devel
    yum install -y oniguruma oniguruma-devel
    yum install -y ImageMagick ImageMagick-devel

    if [ "$OSNAME" == "fedora"  ]; then
        dnf install libxml2 libxml2-devel -y

    fi
fi

##### common start #####

# Install_Libiconv

# Install_Libmemcached
# Install_Curl
# Install_Zlib

# Install_Freetype
# Install_Freetype_New

# Install_OpenSSL
# Install_Libzip

##### common end #####

