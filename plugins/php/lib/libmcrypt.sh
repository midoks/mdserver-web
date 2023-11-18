#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

# echo $rootPath

SERVER_ROOT=$rootPath/lib
SOURCE_ROOT=$rootPath/source/lib


ISFIND="0"
SYS_DIR=(/usr/local /usr)
for S_DIR in ${SYS_DIR[@]}; do
    if [ -f $S_DIR/include/mcrypt.h ];then
        ISFIND="1"
    fi
done

if [ $ISFIND == "0" ];then
    cd $SOURCE_ROOT
    if [ ! -f ${SOURCE_ROOT}/libmcrypt-2.5.8.tar.gz ];then
        wget --no-check-certificate -O libmcrypt-2.5.8.tar.gz  https://sourceforge.net/projects/mcrypt/files/Libmcrypt/2.5.8/libmcrypt-2.5.8.tar.gz -T 20
    fi

    tar -zxvf libmcrypt-2.5.8.tar.gz
    cd libmcrypt-2.5.8
    ./configure && make && make install && make clean

    cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/libmcrypt-2.5.8
fi


# if [ ! -d ${SERVER_ROOT}/libmcrypt ];then

#     cd $SOURCE_ROOT
#     if [ ! -f ${SOURCE_ROOT}/libmcrypt-2.5.8.tar.gz ];then
#         wget -O libmcrypt-2.5.8.tar.gz --no-check-certificate https://sourceforge.net/projects/mcrypt/files/Libmcrypt/2.5.8/libmcrypt-2.5.8.tar.gz -T 20
#     fi

#     tar -zxvf libmcrypt-2.5.8.tar.gz
#     cd libmcrypt-2.5.8

#     ./configure --prefix=${SERVER_ROOT}/libmcrypt && make && make install
# fi