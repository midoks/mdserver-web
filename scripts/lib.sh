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


bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`
echo "${OSNAME}:${VERSION_ID}"

# system judge
if [ "$OSNAME" == "macos" ]; then
    brew install libmemcached
    brew install curl
    brew install zlib
    brew install freetype
    brew install openssl
    brew install libzip
elif [ "$OSNAME" == "opensuse" ];then
    echo "opensuse lib"
elif [ "$OSNAME" == "arch" ];then
    echo "arch lib"
elif [ "$OSNAME" == "freebsd" ];then
    echo "freebsd lib"
elif [ "$OSNAME" == "centos" ];then
    echo "centos lib"
elif [ "$OSNAME" == "fedora" ];then
    echo "fedora lib"
elif [ "$OSNAME" == "alma" ];then
    echo "alma lib"
elif [ "$OSNAME" == "ubuntu"  ] || [ "$OSNAME" == "debian" ]; then
    
    apt install -y devscripts
    apt install -y net-tools
    apt install -y python3-dev
    apt install -y autoconf
    apt install -y gcc

    apt install -y libffi-dev
    apt install -y cmake automake make

    apt install -y webp scons
    apt install -y libwebp-dev
    apt install -y lzma lzma-dev
    apt install -y libunwind-dev

    apt install -y libpcre3 libpcre3-dev 
    apt install -y openssl
    apt install -y libssl-dev
    
    apt install -y libmemcached-dev
    apt install -y libsasl2-dev
    apt install -y imagemagick 
    apt install -y libmagickwand-dev

    apt install -y libxml2 libxml2-dev libbz2-dev libmcrypt-dev libpspell-dev librecode-dev
    apt install -y libgmp-dev libgmp3-dev libreadline-dev libxpm-dev
    apt install -y dia pkg-config
    apt install -y zlib1g-dev
    apt install -y libjpeg-dev libpng-dev
    apt install -y libfreetype6
    apt install -y libjpeg62-turbo-dev
    apt install -y libfreetype6-dev
    apt install -y libevent-dev libncurses5-dev libldap2-dev
    apt install -y libzip-dev
    apt install -y libicu-dev

    apt install -y build-essential
    
    apt install -y libcurl4-openssl-dev
    apt install -y curl libcurl4-gnutls-dev
    #https://blog.csdn.net/qq_36228377/article/details/123154344
    # ln -s  /usr/include/x86_64-linux-gnu/curl  /usr/include/curl
    if [ ! -d /usr/include/curl ];then
        ln -s  /usr/include/x86_64-linux-gnu/curl  /usr/include/curl
    fi
   

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
    echo "OK"
fi


#面板需要的库

if [ ! -f /usr/local/bin/pip3 ];then
    # python3 -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple
    python3 -m pip install --upgrade pip setuptools wheel -i https://pypi.python.org/pypi
fi

pip install --upgrade pip
pip3 install --upgrade setuptools
cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt

pip3 install gevent-websocket==0.10.1
pip3 install flask-caching==1.10.1
# pip3 install mysqlclient


if [ ! -f /www/server/mdserver-web/bin/activate ];then
    cd /www/server/mdserver-web && python3 -m venv .
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate
else
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate
fi

pip install --upgrade pip
pip3 install --upgrade setuptools
pip3 install -r /www/server/mdserver-web/requirements.txt

pip3 install gevent-websocket==0.10.1
pip3 install flask-caching==1.10.1
# pip3 install mysqlclient

