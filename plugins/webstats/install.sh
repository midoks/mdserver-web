#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


## https://www.yangshuaibin.com/detail/392251

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2
sys_os=`uname`

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
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source/webstats
	mkdir -p $serverPath/webstats

	# 下载源码安装包
	# curl -O $serverPath/source/webstats/lua-5.1.5.tar.gz https://www.lua.org/ftp/lua-5.1.5.tar.gz
	# cd $serverPath/source/webstats && tar xvf lua-5.1.5.tar.gz
	# cd lua-5.1.5
	# make linux test && make install

	
	# luarocks
	if [ ! -f $serverPath/source/webstats/luarocks-3.5.0.tar.gz ];then
		wget --no-check-certificate -O $serverPath/source/webstats/luarocks-3.5.0.tar.gz http://luarocks.org/releases/luarocks-3.5.0.tar.gz
	fi
	
	# which luarocks
	# if [ "$?" != "0" ];then
	if [ ! -d $serverPath/webstats/luarocks ];then
		cd $serverPath/source/webstats && tar xvf luarocks-3.5.0.tar.gz
		# cd luarocks-3.9.1 && ./configure && make bootstrap

		cd luarocks-3.5.0 && ./configure --prefix=$serverPath/webstats/luarocks --with-lua-include=$serverPath/openresty/luajit/include/luajit-2.1 --with-lua-bin=$serverPath/openresty/luajit/bin
		make -I${serverPath}/openresty/luajit/bin
		make install 
	fi


	if [ ! -f  $serverPath/source/webstats/lsqlite3_fsl09y.zip ];then
		wget --no-check-certificate -O $serverPath/source/webstats/lsqlite3_fsl09y.zip http://lua.sqlite.org/index.cgi/zip/lsqlite3_fsl09y.zip?uuid=fsl_9y
		cd $serverPath/source/webstats && unzip lsqlite3_fsl09y.zip
	fi

	PATH=${serverPath}/openresty/luajit:${serverPath}/openresty/luajit/include/luajit-2.1:$PATH
	export PATH=$PATH:$serverPath/webstats/luarocks/bin

	if [ ! -f $serverPath/webstats/lua/lsqlite3.so ];then
		if [ "${sys_os}" == "Darwin" ];then
			cd $serverPath/source/webstats/lsqlite3_fsl09y 
			# SQLITE_DIR=/usr/local/Cellar/sqlite/3.36.0
			find_cfg=`cat Makefile | grep 'SQLITE_DIR'`
			if [ "$find_cfg" == "" ];then
				LIB_SQLITE_DIR=`brew info sqlite | grep /usr/local/Cellar/sqlite | cut -d \  -f 1 | awk 'END {print}'`
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
	pip install geoip2
	# if [ ! -f $serverPath/webstats/GeoLite2-City.mmdb ];then
	# 	wget --no-check-certificate -O $serverPath/webstats/GeoLite2-City.mmdb https://github.com/P3TERX/GeoLite.mmdb/releases/download/2022.10.16/GeoLite2-City.mmdb
	# fi

	# 缓存数据
	GEO_VERSION=$(get_latest_release "P3TERX/GeoLite.mmdb")
	if [ ! -f $serverPath/source/webstats/GeoLite2-City.mmdb ];then
		wget --no-check-certificate -O $serverPath/source/webstats/GeoLite2-City.mmdb https://github.com/P3TERX/GeoLite.mmdb/releases/download/${GEO_VERSION}/GeoLite2-City.mmdb
	fi

	if [ -f $serverPath/source/webstats/GeoLite2-City.mmdb ];then
		cp -rf $serverPath/source/webstats/GeoLite2-City.mmdb $serverPath/webstats/GeoLite2-City.mmdb
	fi

	echo "${VERSION}" > $serverPath/webstats/version.pl
	echo '安装完成' > $install_tmp

	cd $rootPath && python3 ${rootPath}/plugins/webstats/index.py start
}

Uninstall_App()
{
	cd $rootPath && python3 ${rootPath}/plugins/webstats/index.py stop
	rm -rf $serverPath/webstats
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
