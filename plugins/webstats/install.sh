#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH=$PATH:/opt/homebrew/bin


## https://www.yangshuaibin.com/detail/392251
# cd /www/server/mdserver-web/plugins/webstats && bash install.sh install 0.2.5
# /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/webstats && bash install.sh install 0.2.5

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2
sys_os=`uname`

HTTP_PREFIX="https://"
LOCAL_ADDR=common
cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
    LOCAL_ADDR=cn
    HTTP_PREFIX="https://"
fi

PIPSRC="https://pypi.python.org/simple"
if [ "$LOCAL_ADDR" != "common" ];then
    PIPSRC="https://pypi.tuna.tsinghua.edu.cn/simple"
fi


if [ "$sys_os" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

get_latest_release() {
    curl -sL "https://api.github.com/repos/$1/releases/latest" | grep '"tag_name":' | cut -d'"' -f4
}

Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source/webstats
	mkdir -p $serverPath/webstats
	echo "${VERSION}" > $serverPath/webstats/version.pl

	# 下载源码安装包
	# curl -O $serverPath/source/webstats/lua-5.1.5.tar.gz https://www.lua.org/ftp/lua-5.1.5.tar.gz
	# cd $serverPath/source/webstats && tar xvf lua-5.1.5.tar.gz
	# cd lua-5.1.5
	# make linux test && make install

	
	# luarocks
	if [ ! -f $serverPath/source/webstats/luarocks-3.5.0.tar.gz ];then
		wget --no-check-certificate -O $serverPath/source/webstats/luarocks-3.5.0.tar.gz http://luarocks.org/releases/luarocks-3.5.0.tar.gz
	fi

	if [ ! -d $serverPath/source/webstats/luarocks-3.5.0  ];then
		cd $serverPath/source/webstats && tar xvf luarocks-3.5.0.tar.gz
	fi

	cd $serverPath/source/webstats/luarocks-3.5.0 && ./configure --prefix=$serverPath/webstats/luarocks \
	--with-lua-include=$serverPath/openresty/luajit/include/luajit-2.1 \
	--with-lua-bin=$serverPath/openresty/luajit/bin
	make -I${serverPath}/openresty/luajit/bin
	make install 


	# lsqlite3_fsl09y
	if [ ! -f $serverPath/source/webstats/lsqlite3_fsl09y.zip ];then
		wget --no-check-certificate -O $serverPath/source/webstats/lsqlite3_fsl09y.zip http://lua.sqlite.org/index.cgi/zip/lsqlite3_fsl09y.zip?uuid=fsl_9y
		
	fi

	if [ ! -d $serverPath/source/webstats/lsqlite3_fsl09y ];then
		cd $serverPath/source/webstats && unzip lsqlite3_fsl09y.zip
	fi

	PATH=${serverPath}/openresty/luajit:${serverPath}/openresty/luajit/include/luajit-2.1:$PATH
	export PATH=$PATH:$serverPath/webstats/luarocks/bin

	if [ ! -f $serverPath/webstats/lua/lsqlite3.so ];then
		if [ "${sys_os}" == "Darwin" ];then
			cd $serverPath/source/webstats/lsqlite3_fsl09y 
			# SQLITE_DIR=/usr/local/Cellar/sqlite/3.36.0
			BREW_DIR=`which brew`
			BREW_DIR=${BREW_DIR/\/bin\/brew/}
			echo "BREW_DIR:"${BREW_DIR}
			find_cfg=`cat Makefile | grep 'SQLITE_DIR'`
			if [ "$find_cfg" == "" ];then
				LIB_SQLITE_DIR=`brew info sqlite | grep ${BREW_DIR}/Cellar/sqlite | cut -d \  -f 1 | awk 'END {print}'`
				echo "LIB_SQLITE_DIR:"${LIB_SQLITE_DIR}
				sed -i $BAK "s#\$(ROCKSPEC)#\$(ROCKSPEC) SQLITE_DIR=${LIB_SQLITE_DIR}#g"  Makefile
			fi
			make
		else
			cd $serverPath/source/webstats/lsqlite3_fsl09y && make
		fi
	fi

	# copy to code path
	DEFAULT_DIR=$serverPath/webstats/luarocks/lib/lua/5.1
	if [ -f ${DEFAULT_DIR}/lsqlite3.so ];then
		mkdir -p $serverPath/webstats/lua
		cp -rf ${DEFAULT_DIR}/lsqlite3.so $serverPath/webstats/lua/lsqlite3.so 
	fi

	# https://github.com/P3TERX/GeoLite.mmdb
	pip install geoip2 -i $PIPSRC
	# if [ ! -f $serverPath/webstats/GeoLite2-City.mmdb ];then
	# 	wget --no-check-certificate -O $serverPath/webstats/GeoLite2-City.mmdb https://github.com/P3TERX/GeoLite.mmdb/releases/download/2022.10.16/GeoLite2-City.mmdb
	# fi

	# 缓存数据
	GEO_VERSION=$(get_latest_release "P3TERX/GeoLite.mmdb")
	if [ ! -f $serverPath/source/webstats/GeoLite2-City.mmdb ];then
		if [ "$LOCAL_ADDR" == "cn" ];then
			wget --no-check-certificate -O $serverPath/source/webstats/GeoLite2-City.mmdb https://dl.midoks.icu/soft/webstats/GeoLite2-City.mmdb
		else
			wget --no-check-certificate -O $serverPath/source/webstats/GeoLite2-City.mmdb https://github.com/P3TERX/GeoLite.mmdb/releases/download/${GEO_VERSION}/GeoLite2-City.mmdb
		fi
	fi

	if [ -f $serverPath/source/webstats/GeoLite2-City.mmdb ];then
		cp -rf $serverPath/source/webstats/GeoLite2-City.mmdb $serverPath/webstats/GeoLite2-City.mmdb
	fi

	cd $rootPath && python3 ${rootPath}/plugins/webstats/index.py start

	echo '网站统计安装完成'

	# delete install data
	if [ -d $serverPath/source/webstats/lsqlite3_fsl09y ];then
		rm -rf $serverPath/source/webstats/lsqlite3_fsl09y
	fi
	if [ -d $serverPath/source/webstats/luarocks-3.5.0 ];then
		rm -rf $serverPath/source/webstats/luarocks-3.5.0
	fi
}

Uninstall_App()
{
	cd $rootPath && python3 ${rootPath}/plugins/webstats/index.py stop
	rm -rf $serverPath/webstats
	echo "网站统计卸载完成"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
