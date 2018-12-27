#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

#https://dev.mysql.com/downloads/mysql/5.5.html#downloads
#https://dev.mysql.com/downloads/file/?id=480541

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
		wget -O ${mysqlDir}/mysql-5.5.62.tar.gz https://dev.mysql.com/get/Downloads/MySQL-5.5/mysql-5.5.62.tar.gz
	fi

	if [ ! -f ${mysqlDir}/mysql-5.5.62 ];then
		 cd ${mysqlDir} && tar -zxvf  ${mysqlDir}/mysql-5.5.62.tar.gz
	fi
	

	cd ${mysqlDir}/mysql-5.5.62 && cmake \
	-DCMAKE_INSTALL_PREFIX=$serverPath/mysql \
	&& make && make install && make clean \
	&& echo '5.5' > $serverPath/mysql/version.pl
	echo '安装完成' > $install_tmp
}

Uninstall_mysql()
{
	#rm -rf $serverPath/mysql
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_mysql
else
	Uninstall_mysql
fi
