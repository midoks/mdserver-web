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
		cp -rf ${SOLR_DIR}/solr-8.2.0/ $serverPath/solr
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
