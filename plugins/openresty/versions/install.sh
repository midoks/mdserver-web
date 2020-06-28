#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


VERSION=$1

install_tmp=${rootPath}/tmp/mw_install.pl
openrestyDir=${serverPath}/source/openresty

Install_openresty()
{
	mkdir -p ${openrestyDir}
	echo '正在安装脚本文件...' > $install_tmp

	if [ ! -f ${openrestyDir}/openresty-${VERSION}.tar.gz ];then
		wget -O ${openrestyDir}/openresty-${VERSION}.tar.gz https://openresty.org/download/openresty-${VERSION}.tar.gz
	fi


	cd ${openrestyDir} && tar -zxvf openresty-${VERSION}.tar.gz

	cd ${openrestyDir}/openresty-${VERSION} && ./configure --prefix=$serverPath/openresty \
	--with-http_v2_module \
	--with-openssl=$serverPath/source/lib/openssl-1.0.2q  \
	--with-http_stub_status_module && make && make install && \
	echo "${VERSION}" > $serverPath/openresty/version.pl
	

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
