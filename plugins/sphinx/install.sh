#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl


sysName=`uname`
echo "use system: ${sysName}"

if [ ${sysName} == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
	OSNAME='raspbian'
else
	OSNAME='unknow'
fi

if [ ${OSNAME} == "centos" ] || [ ${OSNAME} == "fedora" ]; then
	yum install -y postgresql-libs unixODBC
fi




Install_sphinx()
{

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/sphinx

	SPHINX_DIR=${serverPath}/source/sphinx
	mkdir -p $SPHINX_DIR
	if [ ! -f ${SPHINX_DIR}/sphinx-3.1.1.tar.gz ];then
		if [ $sysName == 'Darwin' ]; then
			wget -O ${SPHINX_DIR}/sphinx-3.1.1.tar.gz http://sphinxsearch.com/files/sphinx-3.1.1-612d99f-darwin-amd64.tar.gz
		else
			wget -O ${SPHINX_DIR}/sphinx-3.1.1.tar.gz http://sphinxsearch.com/files/sphinx-3.1.1-612d99f-linux-amd64.tar.gz
		fi
	fi

	cd ${SPHINX_DIR} && tar -zxvf sphinx-3.1.1.tar.gz

	cp -rf ${SPHINX_DIR}/sphinx-3.1.1/ $serverPath/sphinx/bin

	echo '3.1.1' > $serverPath/sphinx/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_sphinx()
{
	rm -rf $serverPath/sphinx
	echo "Uninstall_sphinx" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_sphinx
else
	Uninstall_sphinx
fi
