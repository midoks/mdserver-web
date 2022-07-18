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
		wget -O $serverPath/source/webstats/luarocks-3.5.0.tar.gz https://luarocks.org/releases/luarocks-3.5.0.tar.gz
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
		wget -O $serverPath/source/webstats/lsqlite3_fsl09y.zip http://lua.sqlite.org/index.cgi/zip/lsqlite3_fsl09y.zip?uuid=fsl_9y
		cd $serverPath/source/webstats && unzip lsqlite3_fsl09y.zip
	fi

	# PATH=${serverPath}/openresty/luajit:${serverPath}/openresty/luajit/include/luajit-2.1:$PATH
	# export PATH=$PATH:$serverPath/webstats/luarocks/bin
	# cd $serverPath/source/webstats/lsqlite3_fsl09y && make


	# if [ ! -d $serverPath/source/webstats/luasql-2.6.0 ];then
	# 	wget -O $serverPath/source/webstats/luasql_2.6.0.tar.gz https://github.com/keplerproject/luasql/archive/refs/tags/2.6.0.tar.gz
	# 	cd $serverPath/source/webstats && tar xvf luasql_2.6.0.tar.gz
	# fi

	# PATH=${serverPath}/openresty/luajit:${serverPath}/openresty/luajit/include/luajit-2.1:$PATH
	# export PATH
	# export LUA_INCDIR=${serverPath}/openresty/luajit/include/luajit-2.1
	# cd $serverPath/source/webstats/luasql-2.6.0 && make sqlite3
	
	# $serverPath/webstats/luarocks/bin/luarocks config --scope user lib_modules_path ${serverPath}/openresty/luajit/lib
	# $serverPath/webstats/luarocks/bin/luarocks config --scope user lib_modules_path
	# $serverPath/webstats/luarocks/bin/luarocks install lua-sqlite3
	$serverPath/webstats/luarocks/bin/luarocks install luasql-sqlite3 SQLITE_DIR=$serverPath/webstats/lua


	echo "${VERSION}" > $serverPath/webstats/version.pl
	echo '安装完成' > $install_tmp
	# cd $rootPath && python3 ${rootPath}/plugins/webstats/index.py start
}

Uninstall_App()
{
	rm -rf $serverPath/webstats
	echo "Uninstall_redis" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
