#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# https://blog.csdn.net/akipa11/article/details/103455298
# https://blog.csdn.net/bbj12345678/article/details/122941395

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

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
	which "java" > /dev/null
	if [ $? -eq 0 ]
	then
    	echo 'java is exist'
    elif [ "ubuntu" == "$OSNAME" ] || [ "debian" == "$OSNAME" ] ;then
    	echo 'java install...'
    	apt install -y default-jdk

    	export JAVA_HOME=/usr/lib/jvm/default-java
	else
    	echo 'java install...'
    	yum install -y java
	fi
}

# export JAVA_HOME=/usr/lib/jvm/default-java
#JAVA_BIN=/usr/lib/jvm/default-java/bin
#JRE_HOME=/usr/lib/jvm/default-java/jre
#PATH=$PATH:/usr/lib/jvm/default-java/bin:/usr/lib/jvm/default-java/jre/bin
#CLASSPATH=/usr/lib/jvm/default-java/jre/lib:/usr/lib/jvm/default-java/lib:/usr/lib/jvm/default-java/jre/lib/charsets.jar


Install_csvn()
{
	CheckJAVA
	mkdir -p $serverPath/source

	echo '正在安装脚本文件...' > $install_tmp

	CSVN_SOURCE='https://github.com/midoks/mdserver-web/releases/download/init/CollabNetSubversionEdge-5.1.4_linux-x86_64.tar.xz'

	if [ ! -f $serverPath/source/csvn.tar.xz ];then
		wget -O $serverPath/source/csvn.tar.xz ${CSVN_SOURCE}
	fi

	cd $serverPath/source && tar -Jxf $serverPath/source/csvn.tar.xz
	mv $serverPath/source/csvn $serverPath/csvn
	echo '5.1' > $serverPath/csvn/version.pl


	if id -u csvn > /dev/null 2>&1; then
        echo "csvn user exists"
	else
		groupadd csvn
		useradd -g csvn csvn
		cp /etc/sudoers{,.`date +"%Y-%m-%d_%H-%M-%S"`}
		echo "csvn ALL=(ALL)    NOPASSWD: ALL" >> /etc/sudoers
	fi

	chown -R  csvn:csvn $serverPath/csvn

	$serverPath/csvn/bin/csvn install
	$serverPath/csvn/bin/csvn-httpd install
	
	echo '安装完成' > $install_tmp
}

Uninstall_csvn()
{
	rm -rf $serverPath/csvn
}


action=$1
host=$2
if [ "${1}" == 'install' ];then
	Install_csvn
else
	Uninstall_csvn
fi
