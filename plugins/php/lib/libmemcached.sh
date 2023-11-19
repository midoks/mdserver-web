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

#----------------------------- libmemcached start -------------------------#
# if [ ! -d ${SERVER_ROOT}/libmemcached ];then
#     cd ${SOURCE_ROOT}
#     if [ ! -f ${SOURCE_ROOT}/libmemcached-1.0.4.tar.gz ];then
#     	wget -O libmemcached-1.0.4.tar.gz https://launchpad.net/libmemcached/1.0/1.0.4/+download/libmemcached-1.0.4.tar.gz -T 20
#     fi 
#     tar -zxf libmemcached-1.0.4.tar.gz
#     cd libmemcached-1.0.4
#     ./configure --prefix=${SERVER_ROOT}/libmemcached -with-memcached && make && make install
# fi
#----------------------------- libmemcached end -------------------------#


#----------------------------- libmemcached start -------------------------#
if [ ! -d ${SERVER_ROOT}/libmemcached ];then
    cd ${SOURCE_ROOT}
    if [ ! -f ${SOURCE_ROOT}/libmemcached-1.0.18.tar.gz ];then
        wget --no-check-certificate -O libmemcached-1.0.18.tar.gz https://launchpad.net/libmemcached/1.0/1.0.18/+download/libmemcached-1.0.18.tar.gz -T 20
    fi 
    tar -zxf libmemcached-1.0.18.tar.gz
    cd libmemcached-1.0.18

    # sed -i '_bak' "41,52s#opt_servers == false#opt_servers#g" ${SERVER_ROOT}/libmemcached-1.0.18/clients/memflush.cc
    sed -i "s#opt_servers == false#\!opt_servers#g" ${SERVER_ROOT}/libmemcached-1.0.18/clients/memflush.cc
    # sed -i "s#opt_servers == false#\!opt_servers#g" /www/server/source/lib/libmemcached-1.0.18/clients/memflush.cc
    ./configure --prefix=${SERVER_ROOT}/libmemcached -with-memcached && make && make install

    cd $SOURCE_ROOT && rm -rf $SOURCE_ROOT/libmemcached-1.0.18
    
fi
#----------------------------- libmemcached end -------------------------#