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

VERSION=29.9.0
Install_App()
{
	echo '正在安装manticoresearch...'
	mkdir -p $serverPath/manticoresearch

	MC_DIR=${serverPath}/source/manticoresearch
	mkdir -p $MC_DIR

	# https://github.com/manticoresoftware/manticoresearch/archive/refs/tags/release-29.9.0.tar.gz
	MC_SRC=$MC_DIR/manticoresearch-release-${VERSION}
	if [ ! -d $MC_SRC ];then
		if [ ! -f $MC_DIR/release-${VERSION}.tar.gz ];then
			wget -O $MC_DIR/release-${VERSION}.tar.gz "https://github.com/manticoresoftware/manticoresearch/archive/refs/tags/release-${VERSION}.tar.gz"
		fi
		cd $MC_DIR && tar -zxvf release-${VERSION}.tar.gz
	fi

	# 源码包方式没有子模块，单独补全 mcl（子模块地址见 .gitmodules: manticoresoftware/columnar）
	if [ ! -f $MC_SRC/mcl/CMakeLists.txt ];then
		echo 'initializing mcl submodule...'
		rm -rf $MC_SRC/mcl
		MCL_SHA=$(curl -fsSL "https://api.github.com/repos/manticoresoftware/manticoresearch/contents/mcl?ref=release-${VERSION}" 2>/dev/null | grep -o '"sha": *"[0-9a-f]*"' | head -n 1 | sed 's/.*"sha": *"//;s/"//')
		if ! git clone https://github.com/manticoresoftware/columnar.git $MC_SRC/mcl;then
			echo "mcl clone failed!"
			exit 1
		fi
		if [ -n "${MCL_SHA}" ];then
			cd $MC_SRC/mcl && git checkout ${MCL_SHA}
		fi
	fi

	if [ ! -f $MC_SRC/mcl/CMakeLists.txt ];then
		echo "MCL submodule is required at $MC_SRC/mcl."
		exit 1
	fi

	# 上次配置失败残留的 build 目录会保留 FetchContent 失败状态，先清理
	if [ -d $MC_SRC/build ] && [ ! -f $MC_SRC/build/Makefile ];then
		rm -rf $MC_SRC/build
	fi

	mkdir -p $MC_SRC/build
	cd $MC_SRC/build
	cmake .. -DCMAKE_BUILD_TYPE=Release
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