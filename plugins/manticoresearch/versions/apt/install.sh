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
	source ${rootPath}/bin/activate
fi

# cd /www/server/mdserver-web && source bin/activate && python3 plugins/sphinx/index.py rebuild
# cd /www/server/mdserver-web/plugins/sphinx && bash install.sh install 3.6.1
# cd /www/server/mdserver-web && source bin/activate && python3 plugins/sphinx/index.py db_to_sphinx && /www/server/sphinx/bin/bin/indexer -c /www/server/sphinx/sphinx.conf --all --rotate
# /Users/midoks/Desktop/mwdev/server/sphinx/bin/bin/indexer /Users/midoks/Desktop/mwdev/server/sphinx/sphinx.conf --all --rotate

# cd /www/server/mdserver-web && source bin/activate && python3 plugins/sphinx/index.py sphinx_cmd

# /Users/midoks/Desktop/mwdev/server/sphinx/bin/bin/indexer /Users/midoks/Desktop/mwdev/server/sphinx/sphinx.conf --all --rotate

# cd /www/server/mdserver-web && source bin/activate && python3 plugins/sphinx/index.py start
bash ${rootPath}/scripts/getos.sh
# echo "bash ${rootPath}/scripts/getos.sh"
OSNAME="macos"
if [ -f ${rootPath}/data/osname.pl ];then
	OSNAME=`cat ${rootPath}/data/osname.pl`	
fi

if [ "${OSNAME}" == "centos" ] || 
	[ "${OSNAME}" == "fedora" ] ||
	[ "${OSNAME}" == "alma" ]; then
	yum install -y postgresql-libs unixODBC
fi

# http://sphinxsearch.com/files/sphinx-3.7.1-da9f8a4-linux-amd64.tar.gz

VERSION=$2

# echo $VERSION

if [ "$VERSION" == "3.1.1" ];then
	VERSION_NUM=${VERSION}-612d99f
elif [ "$VERSION" == "3.2.1" ]; then
	VERSION_NUM=${VERSION}-f152e0b
elif [ "$VERSION" == "3.3.1" ]; then
	VERSION_NUM=${VERSION}-b72d67b
elif [ "$VERSION" == "3.4.1" ]; then
	VERSION_NUM=${VERSION}-efbcc65
elif [ "$VERSION" == "3.5.1" ]; then
	VERSION_NUM=${VERSION}-82c60cb
elif [ "$VERSION" == "3.6.1" ]; then
	VERSION_NUM=${VERSION}-c9dbeda
elif [ "$VERSION" == "3.7.1" ]; then
	VERSION_NUM=${VERSION}-da9f8a4
elif [ "$VERSION" == "3.8.1" ]; then
	VERSION_NUM=${VERSION}-d25e0bb
fi

# echo $VERSION_NUM

Install_App()
{
	echo '正在安装manticoresearch...'
	mkdir -p $serverPath/manticoresearch

	MC_DIR=${serverPath}/source/manticoresearch
	mkdir -p $MC_DIR

	wget --no-check-certificate -O $MC_DIR/manticore-repo.noarch.deb https://repo.manticoresearch.com/manticore-repo.noarch.deb
	dpkg -i $MC_DIR/manticore-repo.noarch.deb
	apt update
	apt install manticore manticore-extra

	if [ -d ${MC_DIR} ];then
		rm -rf ${MC_DIR}
	fi
}

Uninstall_App()
{
	echo "卸载manticoresearch成功"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
