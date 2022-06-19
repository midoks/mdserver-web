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

CheckJAVA()
{
	which java > /dev/null
	if [ $? -eq 0 ];then
    	echo 'java is exist'
	else
		echo 'java install...'
		if [ "centos" == "$OSNAME" ] || [ "fedora" == "$OSNAME" ];then
	    	yum install -y java
	    elif [ "ubuntu" == "$OSNAME" ] || [ "debian" == "$OSNAME" ] ;then
	    	snap install openjdk
		else
			yum install -y java
		fi
	fi
}



if id solr &> /dev/null ;then 
    echo "solr UID is `id -u solr`"
    echo "solr Shell is `grep "^solr:" /etc/passwd |cut -d':' -f7 `"
else
	if [ "$OSNAME" == "macos" ];then
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
	CheckJAVA
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

	if [ ! -d ${SOLR_DIR}/mmseg4j-${mmseg_version} ];then
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
