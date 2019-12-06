#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
install_tmp=${rootPath}/tmp/mw_install.pl
sysName=`uname`

Install_walle()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/jenkins
	echo '1.0' > $serverPath/jenkins/version.pl


	if [ $sysName == 'Darwin' ]; then
		echo "jenkins mac no install!"
	else
		wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
		rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key
		yum -y install jenkins
	fi

	echo '安装完成' > $install_tmp

}

Uninstall_walle()
{
	rm -rf $serverPath/jenkins
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_walle
else
	Uninstall_walle
fi