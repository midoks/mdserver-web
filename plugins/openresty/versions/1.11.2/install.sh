#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


install_tmp=${rootPath}/tmp/bt_install.pl
openrestyDir=${serverPath}/source/openresty

Install_openresty()
{
	mkdir -p ${openrestyDir}
	echo '正在安装脚本文件...' > $install_tmp

	if [ ! -f ${openrestyDir}/openresty-1.11.2.5.tar.gz ];then
		wget -O ${openrestyDir}/openresty-1.11.2.5.tar.gz https://openresty.org/download/openresty-1.11.2.5.tar.gz
	fi


	cd ${openrestyDir} && tar -zxvf openresty-1.11.2.5.tar.gz

	cd ${openrestyDir}/openresty-1.11.2.5 && ./configure --prefix=$serverPath/openresty \
	--with-openssl=$serverPath/source/lib/openssl-1.0.2q && make && make install && \
	echo '1.11.2' > $serverPath/openresty/version.pl
	

	echo '安装完成' > $install_tmp
}

Uninstall_openresty()
{
	rm -rf $serverPath/openresty
	echo '卸载完成' > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_openresty
else
	Uninstall_openresty
fi
