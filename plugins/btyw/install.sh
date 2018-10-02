#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'
CN='125.88.182.172'
HK='download.bt.cn'
HK2='103.224.251.67'
US='174.139.221.74'
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

Install_btyw()
{
	mkdir -p /www/server/panel/plugin/btyw
	echo '正在安装脚本文件...' > $install_tmp
	wget -O /www/server/panel/plugin/btyw/btyw_main.py $download_Url/install/lib/plugin/btyw/btyw_main.py -T 5
	wget -O /www/server/panel/plugin/btyw/index.html $download_Url/install/lib/plugin/btyw/index.html -T 5
	wget -O /www/server/panel/plugin/btyw/info.json $download_Url/install/lib/plugin/btyw/info.json -T 5
	wget -O /www/server/panel/plugin/btyw/icon.png $download_Url/install/lib/plugin/btyw/icon.png -T 5
	wget -O /www/server/panel/static/img/soft_ico/ico-btyw.png $download_Url/install/lib/plugin/btyw/icon.png -T 5
	wget -O /www/server/panel/static/images/ico-hot.png $download_Url/install/lib/plugin/btyw/ico-hot.png -T 5
	
	echo '安装完成' > $install_tmp
}

Uninstall_btyw()
{
	rm -rf /www/server/panel/plugin/btyw
	pip uninstall btyw -y
}


action=$1
if [ "${1}" == 'install' ];then
	Install_btyw
else
	Uninstall_btyw
fi
