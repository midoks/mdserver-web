#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# cd /www/server/mdserver-web/plugins/op_waf && bash install.sh install 0.4.1

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

action=$1
version=$2
sys_os=`uname`

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

if [ "$sys_os" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi


Install_App(){
	
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source/op_waf
	mkdir -p $serverPath/op_waf

	# luarocks
	if [ ! -f $serverPath/source/op_waf/luarocks-3.5.0.tar.gz ];then
		wget --no-check-certificate -O $serverPath/source/op_waf/luarocks-3.5.0.tar.gz http://luarocks.org/releases/luarocks-3.5.0.tar.gz
	fi
	
	# which luarocks
	if [ ! -d $serverPath/op_waf/luarocks ];then
		cd $serverPath/source/op_waf && tar xvf luarocks-3.5.0.tar.gz
		# cd luarocks-3.9.1 && ./configure && make bootstrap

		cd luarocks-3.5.0 && ./configure --prefix=$serverPath/op_waf/luarocks \
		--with-lua-include=$serverPath/openresty/luajit/include/luajit-2.1 \
		--with-lua-bin=$serverPath/openresty/luajit/bin
		make -I${serverPath}/openresty/luajit/bin
		make install 
	fi


	if [ ! -f $serverPath/source/op_waf/lsqlite3_fsl09y.zip ];then
		wget --no-check-certificate -O $serverPath/source/op_waf/lsqlite3_fsl09y.zip http://lua.sqlite.org/index.cgi/zip/lsqlite3_fsl09y.zip?uuid=fsl_9y
		cd $serverPath/source/op_waf && unzip lsqlite3_fsl09y.zip
	fi

	if [ ! -d $serverPath/source/op_waf/lsqlite3_fsl09y ];then
		cd $serverPath/source/op_waf && unzip lsqlite3_fsl09y.zip
	fi

	PATH=${serverPath}/openresty/luajit:${serverPath}/openresty/luajit/include/luajit-2.1:$PATH
	export PATH=$PATH:$serverPath/op_waf/luarocks/bin

	if [ ! -f $serverPath/op_waf/waf/conf/lsqlite3.so ];then
		if [ "${sys_os}" == "Darwin" ];then
			cd $serverPath/source/op_waf/lsqlite3_fsl09y
			find_cfg=`cat Makefile | grep 'SQLITE_DIR'`
			if [ "$find_cfg" == "" ];then
				LIB_SQLITE_DIR=`brew info sqlite | grep /usr/local/Cellar/sqlite | cut -d \  -f 1 | awk 'END {print}'`
				echo $LIB_SQLITE_DIR
				sed -i $BAK "s#\$(ROCKSPEC)#\$(ROCKSPEC) SQLITE_DIR=${LIB_SQLITE_DIR}#g"  Makefile
			fi
			make
		else
			cd $serverPath/source/op_waf/lsqlite3_fsl09y && make
		fi
	fi

	# copy to code path
	DEFAULT_DIR=$serverPath/op_waf/luarocks/lib/lua/5.1
	if [ -f ${DEFAULT_DIR}/lsqlite3.so ];then
		mkdir -p $serverPath/op_waf/waf/conf
		cp -rf ${DEFAULT_DIR}/lsqlite3.so $serverPath/op_waf/waf/conf/lsqlite3.so
	fi

	cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
	HTTP_PREFIX="https://"
	if [ ! -z "$cn" ];then
	    HTTP_PREFIX="https://mirror.ghproxy.com/"
	fi

	# download GeoLite Data
	GeoLite2_TAG=`curl -sL "https://api.github.com/repos/P3TERX/GeoLite.mmdb/releases/latest" | grep '"tag_name":' | cut -d'"' -f4`
	#if [ ! -f $serverPath/op_waf/GeoLite2-City.mmdb ];then
	wget --no-check-certificate -O $serverPath/op_waf/GeoLite2-City.mmdb ${HTTP_PREFIX}github.com/P3TERX/GeoLite.mmdb/releases/download/${GeoLite2_TAG}/GeoLite2-City.mmdb
	#fi

	#if [ ! -f $serverPath/op_waf/GeoLite2-Country.mmdb ];then
	wget --no-check-certificate -O $serverPath/op_waf/GeoLite2-Country.mmdb ${HTTP_PREFIX}github.com/P3TERX/GeoLite.mmdb/releases/download/${GeoLite2_TAG}/GeoLite2-Country.mmdb
	#fi

	libmaxminddb_ver='1.7.1'
	if [ ! -f $serverPath/op_waf/waf/mmdb/lib/libmaxminddb.a ] && [ ! -f $serverPath/op_waf/waf/mmdb/lib/libmaxminddb.so ];then
		libmaxminddb_local_path=$serverPath/source/op_waf/libmaxminddb-${libmaxminddb_ver}.tar.gz
		libmaxminddb_url_path=${HTTP_PREFIX}github.com/maxmind/libmaxminddb/releases/download/${libmaxminddb_ver}/libmaxminddb-${libmaxminddb_ver}.tar.gz
		if [ ! -f ${libmaxminddb_local_path} ]; then
			wget --no-check-certificate -O ${libmaxminddb_local_path} ${libmaxminddb_url_path}
		fi

		cd $serverPath/source/op_waf && tar -zxvf ${libmaxminddb_local_path} && \
		cd $serverPath/source/op_waf/libmaxminddb-${libmaxminddb_ver} && \
		./configure --prefix=$serverPath/op_waf/waf/mmdb && make && make install
	fi

	echo "${version}" > $serverPath/op_waf/version.pl
	echo 'install ok' > $install_tmp

	cd ${rootPath} && python3 ${rootPath}/plugins/op_waf/index.py start
	echo "cd ${rootPath} && python3 ${rootPath}/plugins/op_waf/index.py start"
	sleep 2
	cd ${rootPath} && python3 ${rootPath}/plugins/op_waf/index.py reload
}

Uninstall_App(){

	cd ${rootPath} && python3 ${rootPath}/plugins/op_waf/index.py stop
	if [ "$?" == "0" ];then
		rm -rf $serverPath/op_waf
	fi
}


action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
