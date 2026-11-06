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

# 下载文件，直连失败时走加速镜像
download_file()
{
	src=$1
	dst=$2
	for url in "$src" "https://ghproxy.net/$src" "https://gh-proxy.com/$src" "https://ghfast.top/$src"
	do
		if curl -fsSL --retry 2 --connect-timeout 20 -o "$dst" "$url";then
			return 0
		fi
		rm -f "$dst"
	done
	return 1
}

Install_App()
{
	echo '正在安装manticoresearch...'
	mkdir -p $serverPath/manticoresearch
	echo "${VERSION}" > $serverPath/manticoresearch/version.pl

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

	# 预先下载 CRoaring，交给 cmake 的 FetchContent 直接使用本地源码
	ROARING_VER=4.3.2
	ROARING_SRC=$MC_DIR/deps/CRoaring-${ROARING_VER}
	if [ ! -d $ROARING_SRC ];then
		mkdir -p $MC_DIR/deps
		ROARING_TGZ=$MC_DIR/deps/roaring-v${ROARING_VER}.tar.gz
		if [ ! -s $ROARING_TGZ ];then
			if ! download_file "https://github.com/RoaringBitmap/CRoaring/archive/refs/tags/v${ROARING_VER}.tar.gz" "$ROARING_TGZ";then
				echo "roaring download failed!"
				exit 1
			fi
		fi
		tar -zxvf $ROARING_TGZ -C $MC_DIR/deps
	fi

	if [ ! -f $ROARING_SRC/CMakeLists.txt ];then
		echo "roaring source is required at $ROARING_SRC."
		exit 1
	fi

	# CRoaring 默认会下载 CPM.cmake 并拉取 cmocka（仅测试用），网络受限时会配置失败；
	# 关闭 CPM 与测试，只编译 roaring 库本体
	if ! grep -q 'MWSET_ROARING_PATCHED' $ROARING_SRC/CMakeLists.txt;then
		sed -i "s/^option(ENABLE_ROARING_TESTS.*$/set(ENABLE_ROARING_TESTS OFF CACHE BOOL \"\" FORCE) # MWSET_ROARING_PATCHED/" $ROARING_SRC/CMakeLists.txt
		sed -i "s/^option(ROARING_USE_CPM.*$/set(ROARING_USE_CPM OFF CACHE BOOL \"\" FORCE)/" $ROARING_SRC/CMakeLists.txt
	fi

	# 上次配置失败残留的 build 目录会保留 FetchContent/galera 的失败状态，先清理
	if [ -d $MC_SRC/build ];then
		if [ ! -f $MC_SRC/build/Makefile ] || grep -q 'WITH_GALERA:BOOL=ON' $MC_SRC/build/CMakeCache.txt 2>/dev/null;then
			rm -rf $MC_SRC/build
		fi
	fi

	mkdir -p $MC_SRC/build
	cd $MC_SRC/build
	# embeddings 库需要 Rust(cargo)：没有则先尝试安装，失败再关闭本地编译（功能可选）
	if ! command -v cargo >/dev/null 2>&1;then
		if [ -x "$HOME/.cargo/bin/cargo" ];then
			PATH="$HOME/.cargo/bin:$PATH"
			export PATH
		else
			echo 'installing rust toolchain...'
			if curl -fsSL --connect-timeout 20 https://sh.rustup.rs | sh -s -- -y --profile minimal;then
				PATH="$HOME/.cargo/bin:$PATH"
				export PATH
			fi
		fi
	fi
	EMBEDDINGS_FLAG=""
	if ! command -v cargo >/dev/null 2>&1;then
		echo "cargo not found, disable local embeddings build"
		EMBEDDINGS_FLAG="-DBUILD_EMBEDDINGS_LOCALLY=OFF"
	fi
	# 编译需要 Boost 的 context/filesystem 组件（静止库），缺 dev 包时 cmake 会报 boost_context 找不到
	if command -v apt >/dev/null 2>&1;then
		apt install -y --no-install-recommends libboost-context-dev libboost-filesystem-dev libboost-system-dev libboost-thread-dev >/dev/null 2>&1
	fi
	# galera 依赖 boost_system 开发包，源码安装统一关闭；不需要 galera 复制功能
	cmake .. -DCMAKE_BUILD_TYPE=Release \
		-DWITH_GALERA=OFF \
		$EMBEDDINGS_FLAG \
		-DFETCHCONTENT_SOURCE_DIR_ROARING="$ROARING_SRC" \
		-DCMAKE_INSTALL_PREFIX=/usr/local
	if [ ! -f Makefile ];then
		echo "manticoresearch cmake configure failed!"
		exit 1
	fi

	JOBS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
	if ! make -j${JOBS};then
		echo "manticoresearch build failed!"
		exit 1
	fi

	# 安装二进制到面板目录并软链到 /usr/local/bin，保证 indexer/searchd 在 PATH 中
	BIN_DIR=$serverPath/manticoresearch/bin
	mkdir -p $BIN_DIR
	for b in searchd indexer indextool;do
		if [ -f $MC_SRC/build/src/$b ];then
			cp -f $MC_SRC/build/src/$b $BIN_DIR/$b
			chmod +x $BIN_DIR/$b
			ln -sf $BIN_DIR/$b /usr/local/bin/$b
		fi
	done

	# 插件要求 manticore 用户存在
	if ! id manticore >/dev/null 2>&1;then
		useradd -r -s /bin/false -d $serverPath/manticoresearch manticore
	fi

	# 源码安装没有 deb 包自带的 systemd 服务，这里补一个
	if [ ! -f /lib/systemd/system/manticore.service ] && [ ! -f /usr/lib/systemd/system/manticore.service ];then
		cat > /lib/systemd/system/manticore.service <<'EOF'
[Unit]
Description=Manticore Search
After=network.target

[Service]
Type=simple
User=manticore
Group=manticore
ExecStart=/usr/local/bin/searchd -c /etc/manticoresearch/manticore.conf
ExecStop=/usr/local/bin/searchd -c /etc/manticoresearch/manticore.conf --stopwait
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
		systemctl daemon-reload
	fi

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