#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl
mysqlDir=${serverPath}/source/mysql

Install_mysql()
{
	mkdir -p ${mysqlDir}
	echo '正在安装脚本文件...' > $install_tmp

	if [ ! -f ${mysqlDir}/mysql-5.5.62.tar.gz ];then
		wget -O ${mysqlDir}/mysql-5.5.62.tar.gz https://github.com/mysql/mysql-server/archive/mysql-5.5.62.tar.gz
	fi


	cd ${mysqlDir} && tar -zxvf mysql-5.5.62.tar.gz

	# cd ${mysqlDir}/mysql-5.5.62 && ./configure --prefix=$serverPath/mysql \
	# --with-openssl=$serverPath/source/lib/openssl-1.0.2q  \
	# --with-http_stub_status_module && make && make install && \
	echo '5.5' > $serverPath/mysql/version.pl

	echo '安装完成' > $install_tmp
}

Uninstall_mysql()
{
	rm -rf $serverPath/mysql
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_mysql
else
	Uninstall_mysql
fi
