#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl

action=$1
version=$2
Install_solr()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/solr
	SOLR_DIR=${serverPath}/source/solr
	mkdir -p $SOLR_DIR
	if [ ! -f ${SOLR_DIR}/solr-8.2.0.tgz ];then
		wget -O ${SOLR_DIR}/solr-8.2.0.tgz http://mirror.bit.edu.cn/apache/lucene/solr/8.2.0/solr-8.2.0.tgz
	fi

	if [ ! -d $serverPath/solr/bin ];then
		cd ${SOLR_DIR} && tar -zxvf solr-8.2.0.tgz
		cp -rf ${SOLR_DIR}/solr-8.2.0/* $serverPath/solr/
		chown -R www:www $serverPath/solr
	fi

	if [ -d $serverPath/solr/dist ]; then
		wget -O $serverPath/solr/dist/mysql-connector-java-5.1.48.jar http://central.maven.org/maven2/mysql/mysql-connector-java/5.1.48/mysql-connector-java-5.1.48.jar
		wget -O $serverPath/solr/dist/mysql-connector-java-8.0.17.jar http://central.maven.org/maven2/mysql/mysql-connector-java/8.0.17/mysql-connector-java-8.0.17.jar
	fi
	
	echo "$version" > $serverPath/solr/version.pl
	echo '安装完成' > $install_tmp

}

Uninstall_solr()
{
	rm -rf $serverPath/solr
	echo "卸载完成" > $install_tmp
}


if [ "${1}" == 'install' ];then
	Install_solr $version
else
	Uninstall_solr $version
fi
