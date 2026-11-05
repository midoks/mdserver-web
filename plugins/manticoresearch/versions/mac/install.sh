#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`
sysArch=`arch`

if [ -f ${rootPath}/bin/activate ];then
	. ${rootPath}/bin/activate
fi

VERSION=$2
action=$1

if [ "${VERSION}" = "latest" ] || [ -z "${VERSION}" ];then
	VERSION=$(curl -fsSL https://api.github.com/repos/manticoresoftware/manticoresearch/releases/latest 2>/dev/null | grep -o '"tag_name": *"release-[^"]*"' | head -n 1 | sed 's/.*release-//;s/"//')
	if [ -z "${VERSION}" ];then
		VERSION=29.9.0
	fi
fi

Install_App()
{
	echo '正在安装manticoresearch...'
	mkdir -p $serverPath/manticoresearch

	MC_DIR=${serverPath}/source/manticoresearch
	mkdir -p $MC_DIR

	# https://github.com/manticoresoftware/manticoresearch/archive/refs/tags/release-29.9.0.tar.gz
	MC_SRC=$MC_DIR/manticoresearch-release-${VERSION}
	if [ ! -d $MC_SRC ];then
		# 必须带 --recursive，否则缺少 mcl 子模块会导致 cmake 失败
		if ! git clone --depth 1 --branch release-${VERSION} --recursive \
			https://github.com/manticoresoftware/manticoresearch.git $MC_SRC;then
			rm -rf $MC_SRC
			if [ ! -f $MC_DIR/release-${VERSION}.tar.gz ];then
				wget --no-check-certificate -O $MC_DIR/release-${VERSION}.tar.gz https://github.com/manticoresoftware/manticoresearch/archive/refs/tags/release-${VERSION}.tar.gz
			fi
			cd $MC_DIR && tar -zxvf release-${VERSION}.tar.gz
		fi
	fi

	# 源码包方式没有子模块，单独补全 mcl
	if [ ! -d $MC_SRC/mcl ];then
		echo 'initializing mcl submodule...'
		git clone --depth 1 https://github.com/manticoresoftware/mcl.git $MC_SRC/mcl
	fi

	mkdir -p $MC_SRC/build
	cd $MC_SRC/build
	cmake .. -DBOOST_ROOT="$(brew --prefix boost)" \
	 	-DCMAKE_PREFIX_PATH="$(brew --prefix boost);$(brew --prefix icu4c@79);$(brew --prefix openssl@3)" \
	 	-DICU_ROOT="$(brew --prefix icu4c@79)" \
	 	-DOPENSSL_ROOT_DIR="$(brew --prefix openssl@3)" \
	 	-DDISTR=macos \
	 	-DWITH_GALERA=OFF
	if [ ! -f Makefile ];then
		echo "manticoresearch cmake configure failed!"
		exit 1
	fi

	JOBS=$(sysctl -n hw.ncpu 2>/dev/null || echo 4)
	if ! make -j${JOBS};then
		echo "manticoresearch build failed!"
		exit 1
	fi


	echo "${VERSION}" > $serverPath/manticoresearch/version.pl
	cd ${rootPath} && python3 plugins/manticoresearch/index.py start ${VERSION}
	cd ${rootPath} && python3 plugins/manticoresearch/index.py initd_install ${VERSION}


	# if [ -d $MC_DIR/manticoresearch-release-${VERSION} ];then
	# 	rm -rf $MC_DIR/manticoresearch-release-${VERSION}
	# fi
	echo "install manticoresearch successful!"
}

Uninstall_App()
{
	cd ${rootPath} && python3 plugins/manticoresearch/index.py stop ${VERSION}
	cd ${rootPath} && python3 plugins/manticoresearch/index.py initd_uninstall ${VERSION}

	if [ -d $serverPath/manticoresearch ];then
		rm -rf $serverPath/manticoresearch
	fi
	
	if [ -f /usr/lib/systemd/system/manticore.service ] || [ -f /lib/systemd/system/manticore.service ];then
		systemctl stop manticore
		systemctl disable manticore
		rm -rf /usr/lib/systemd/system/manticore.service
		rm -rf /lib/systemd/system/manticore.service
		systemctl daemon-reload
	fi

	echo "uninstall manticoresearch successful!"
}

if [ "${1}" = 'install' ] || [ "$action" = "upgrade" ];then
	Install_App
elif [ "${1}" = 'uninstall' ];then
	Uninstall_App
else
	echo "OPTIONS ERROR"
fi