#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl

# cd /www/server/mdserver-web && source bin/activate && python3 plugins/sphinx/index.py rebuild

# cd /www/server/mdserver-web && source bin/activate && python3 plugins/sphinx/index.py db_to_sphinx
# /www/server/sphinx/bin/bin/indexer -c /www/server/sphinx/sphinx.conf 99cms_mc_comic --rotate
# /Users/midoks/Desktop/mwdev/server/sphinx/bin/bin/indexer /Users/midoks/Desktop/mwdev/server/sphinx/sphinx.conf 99cms_mc_comic --rotate

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

if [ ${OSNAME} == "centos" ] || 
	[ ${OSNAME} == "fedora" ] ||
	[ ${OSNAME} == "alma" ]; then
	yum install -y postgresql-libs unixODBC
fi


VERSION=3.1.1
Install_sphinx()
{

	echo '正在安装Sphinx...'
	mkdir -p $serverPath/sphinx

	SPHINX_DIR=${serverPath}/source/sphinx
	mkdir -p $SPHINX_DIR
	
	if [ ! -f ${SPHINX_DIR}/sphinx-${VERSION}.tar.gz ];then
		if [ $sysName == 'Darwin' ]; then
			wget -O ${SPHINX_DIR}/sphinx-${VERSION}.tar.gz http://sphinxsearch.com/files/sphinx-${VERSION}-612d99f-darwin-amd64.tar.gz
		else
			curl -sSLo ${SPHINX_DIR}/sphinx-${VERSION}.tar.gz http://sphinxsearch.com/files/sphinx-${VERSION}-612d99f-linux-amd64.tar.gz
		fi
	fi

	if [ ! -f ${SPHINX_DIR}/sphinx-${VERSION}.tar.gz ];then
		curl -sSLo ${SPHINX_DIR}/sphinx-${VERSION}.tar.gz https://github.com/midoks/mdserver-web/releases/download/init/sphinx-${VERSION}.tar.gz
	fi


	cd ${SPHINX_DIR} && tar -zxvf sphinx-${VERSION}.tar.gz
	
	if [ "$?" == "0" ];then
		mkdir -p $SPHINX_DIR
		cp -rf ${SPHINX_DIR}/sphinx-${VERSION}/ $serverPath/sphinx/bin
	fi
	
	if [ -d $serverPath/sphinx ];then
		echo "${VERSION}" > $serverPath/sphinx/version.pl
		echo '安装Sphinx完成'
		cd ${rootPath} && python3 ${rootPath}/plugins/sphinx/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/sphinx/index.py initd_install
	fi

	if [ -d ${SPHINX_DIR}/sphinx-${VERSION} ];then
		rm -rf ${SPHINX_DIR}/sphinx-${VERSION}
	fi
}

Uninstall_sphinx()
{
	if [ -f /usr/lib/systemd/system/sphinx.service ] || [ -f /lib/systemd/system/sphinx.service ];then
		systemctl stop sphinx
		systemctl disable sphinx
		rm -rf /usr/lib/systemd/system/sphinx.service
		rm -rf /lib/systemd/system/sphinx.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/sphinx/initd/sphinx ];then
		$serverPath/sphinx/initd/sphinx stop
	fi

	rm -rf $serverPath/sphinx
	echo "Uninstall_sphinx" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_sphinx
else
	Uninstall_sphinx
fi
