#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'
CN='125.88.182.172'
HK='download.bt.cn'
HK2='103.224.251.67'
US='128.1.164.196'
sleep 0.5;
CN_PING=`ping -c 1 -w 1 $CN|grep time=|awk '{print $7}'|sed "s/time=//"`
HK_PING=`ping -c 1 -w 1 $HK|grep time=|awk '{print $7}'|sed "s/time=//"`
HK2_PING=`ping -c 1 -w 1 $HK2|grep time=|awk '{print $7}'|sed "s/time=//"`
US_PING=`ping -c 1 -w 1 $US|grep time=|awk '{print $7}'|sed "s/time=//"`

echo "$HK_PING $HK" > ping.pl
echo "$HK2_PING $HK2" >> ping.pl
echo "$US_PING $US" >> ping.pl
echo "$CN_PING $CN" >> ping.pl
nodeAddr=`sort -V ping.pl|sed -n '1p'|awk '{print $2}'`
if [ "$nodeAddr" == "" ];then
	nodeAddr=$HK2
fi

download_Url=http://$nodeAddr:5880

Install_Beta()
{
	mkdir -p /www/server/panel/plugin/beta
	f1=/www/server/panel/data/beta.pl
	if [ ! -f "$f1" ];then
		echo 'False' > $f1
	fi
	f2=/www/server/panel/plugin/beta/config.conf
	if [ ! -f "$f2" ];then
		echo 'False' > $f2
	fi
	echo '正在安装脚本文件...' > $install_tmp
	wget -O /www/server/panel/plugin/beta/beta_main.py $download_Url/install/lib/plugin/beta/beta_main.py -T 5
	wget -O /www/server/panel/plugin/beta/index.html $download_Url/install/lib/plugin/beta/index.html -T 5
	wget -O /www/server/panel/plugin/beta/info.json $download_Url/install/lib/plugin/beta/info.json -T 5
	echo '安装完成' > $install_tmp
}

Uninstall_Beta()
{
	rm -rf /www/server/panel/plugin/beta
	rm -f /www/server/panel/data/beta.pl
}


action=$1
if [ "${1}" == 'install' ];then
	Install_Beta
else
	Uninstall_Beta
fi
