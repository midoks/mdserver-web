#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /www/server/mdserver-web/plugins/cryptocurrency_trade && bash install.sh install

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


VERSION=$2

# pip3 install ccxt
if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate	
fi
pip3 install ccxt
pip3 install pandas
pip3 install pandas_ta
pip3 install pyTelegramBotAPI
pip3 install catalyst
pip3 install matplotlib==3.2.2


Install_App()
{
	echo '正在安装脚本文件...'
	mkdir -p $serverPath/source/cryptocurrency_trade
	mkdir -p $serverPath/cryptocurrency_trade
	echo "${VERSION}" > $serverPath/cryptocurrency_trade/version.pl

	if [ ! -f $serverPath/source/cryptocurrency_trade/ta-lib-0.4.0-src.tar.gz ];then
		wget -O $serverPath/source/cryptocurrency_trade/ta-lib-0.4.0-src.tar.gz https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz
	fi

	if [ ! -d $serverPath/source/cryptocurrency_trade/ta-lib ];then
		cd $serverPath/source/cryptocurrency_trade/ta-lib && tar -xzf ta-lib-0.4.0-src.tar.gz
		cd ta-lib && ./configure --prefix=/usr && make && make install
		rm -rf $serverPath/source/cryptocurrency_trade/ta-lib

		pip3 install ta-lib
	fi
	
	cd ${rootPath} && python3 ${rootPath}/plugins/cryptocurrency_trade/index.py start
	echo '安装完成'

}

Uninstall_App()
{
	rm -rf $serverPath/cryptocurrency_trade
	cd ${rootPath} && python3 ${rootPath}/plugins/cryptocurrency_trade/index.py stop
	echo "卸载完成"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
