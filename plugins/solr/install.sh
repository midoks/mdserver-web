#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

install_tmp=${rootPath}/tmp/mw_install.pl



if id solr &> /dev/null ;then 
    echo "solr UID is `id -u solr`"
    echo "solr Shell is `grep "^solr:" /etc/passwd |cut -d':' -f7 `"
else
	if [ "$sysName" == "Darwin" ];then
		echo "mac ..."
		echo "groupadd solr"
		echo "useradd -g solr -s /bin/bash solr"
	else
		groupadd solr
		useradd -g solr -s /bin/bash solr
	fi 
fi

action=$1
version=$2
Install_solr()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/solr
	SOLR_DIR=${serverPath}/source/solr
	mkdir -p $SOLR_DIR
	if [ ! -f ${SOLR_DIR}/solr-${version}.tgz ];then
		wget -O ${SOLR_DIR}/solr-${version}.tgz https://archive.apache.org/dist/lucene/solr/${version}/solr-${version}.tgz
	fi

	mmseg_version=2.4.0
	if [ ! -f ${SOLR_DIR}/mmseg4j-${mmseg_version}.zip ];then
		wget -O ${SOLR_DIR}/mmseg4j-${mmseg_version}.zip https://github.com/midoks/mdserver-web/releases/download/init/mmseg4j-${mmseg_version}.zip
	fi

	if [ ! -d ${SOLR_DIR}/mmseg4j-2.4.0 ];then
		cd ${SOLR_DIR}/ && unzip mmseg4j-${mmseg_version}.zip
	fi

	if [ ! -f ${SOLR_DIR}/mysql-connector-java-5.1.48.jar ];then
		wget -O ${SOLR_DIR}/mysql-connector-java-5.1.48.jar http://central.maven.org/maven2/mysql/mysql-connector-java/5.1.48/mysql-connector-java-5.1.48.jar
	fi

	if [ ! -f ${SOLR_DIR}/mysql-connector-java-8.0.17.jar ];then
		wget -O ${SOLR_DIR}/mysql-connector-java-8.0.17.jar http://central.maven.org/maven2/mysql/mysql-connector-java/8.0.17/mysql-connector-java-8.0.17.jar
	fi

	if [ ! -d $serverPath/solr/bin ];then
		cd ${SOLR_DIR} && tar -zxvf solr-${version}.tgz
		cp -rf ${SOLR_DIR}/solr-${version}/* $serverPath/solr/
		if [ "$sysName" == "Darwin" ];then
			echo "mac ... chown -R solr:solr $serverPath/solr"
		else
			chown -R solr:solr $serverPath/solr
		fi
		
	fi

	if [ -d $serverPath/solr/dist ]; then

		if [ -f ${SOLR_DIR}/mysql-connector-java-5.1.48.jar ];then
			cp -rf ${SOLR_DIR}/mysql-connector-java-5.1.48.jar $serverPath/solr/dist/
		fi

		if [ -f ${SOLR_DIR}/mysql-connector-java-8.0.17.jar ];then
			cp -rf ${SOLR_DIR}/mysql-connector-java-8.0.17.jar $serverPath/solr/dist/
		fi

		if [ ! -f $serverPath/solr/dist/mmseg4j-core-1.10.0.jar ];then
			cp -rf ${SOLR_DIR}/mmseg4j-2.4.0/mmseg4j-core-1.10.0.jar $serverPath/solr/dist/
		fi

		if [ ! -f $serverPath/solr/dist/mmseg4j-solr-2.4.0.jar ];then
			cp -rf ${SOLR_DIR}/mmseg4j-2.4.0/mmseg4j-solr-2.4.0.jar $serverPath/solr/dist/
		fi
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
