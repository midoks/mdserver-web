#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin

function version_gt() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" != "$1"; }
function version_le() { test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" == "$1"; }
function version_lt() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" != "$1"; }
function version_ge() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" == "$1"; }

P_VER=`python3 -V | awk '{print $2}'`
echo "python:$P_VER"
sleep 1

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
elif [ "$OSNAME" == "rocky" ]; then
    echo "rocky lib"
elif [ "$OSNAME" == "fedora" ];then
    echo "fedora lib"
elif [ "$OSNAME" == "alma" ];then
    echo "alma lib"
elif [ "$OSNAME" == "ubuntu" ];then
    echo "ubuntu lib"
elif [ "$OSNAME" == "debian" ]; then
    echo "debian lib"
else
    echo "OK"
fi


# HTTP_PREFIX="https://"
# LOCAL_ADDR=common
# ping  -c 1 github.com > /dev/null 2>&1
# if [ "$?" != "0" ];then
#   LOCAL_ADDR=cn
#   HTTP_PREFIX="https://mirror.ghproxy.com/"
# fi
HTTP_PREFIX="https://"
LOCAL_ADDR=common
cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
    LOCAL_ADDR=cn
    HTTP_PREFIX="https://mirror.ghproxy.com/"
fi

PIPSRC="https://pypi.python.org/simple"
if [ "$LOCAL_ADDR" != "common" ];then
    PIPSRC="https://pypi.tuna.tsinghua.edu.cn/simple"
fi

echo "local:${LOCAL_ADDR}"
echo "pypi source:$PIPSRC"

#面板需要的库
if [ ! -f /usr/local/bin/pip3 ] && [ ! -f /usr/bin/pip3 ];then
    python3 -m pip install --upgrade pip setuptools wheel -i $PIPSRC

    which pip3 && pip3 install --upgrade pip -i $PIPSRC
    pip3 install --upgrade pip setuptools wheel -i $PIPSRC
fi

if [ ! -f /www/server/mdserver-web/bin/activate ];then
    if version_ge "$P_VER" "3.11.0" ;then
        cd /www/server/mdserver-web && python3 -m venv /www/server/mdserver-web
    else
        cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt -i $PIPSRC
        cd /www/server/mdserver-web && python3 -m venv .
    fi
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate
else
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate
fi

pip3 install --upgrade pip -i $PIPSRC
pip3 install --upgrade setuptools -i $PIPSRC

# --no-cache-dir
cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt -i $PIPSRC


# Different versions use different python lib
P_VER_D=`echo "$P_VER"|awk -F '.' '{print $1}'`
P_VER_M=`echo "$P_VER"|awk -F '.' '{print $2}'`
NEW_P_VER=${P_VER_D}.${P_VER_M}

if [ -f /www/server/mdserver-web/version/r${NEW_P_VER}.txt ];then
    echo "cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/version/r${NEW_P_VER}.txt"
    cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/version/r${NEW_P_VER}.txt -i $PIPSRC
fi

echo "lib ok!"