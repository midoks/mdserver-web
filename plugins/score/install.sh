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
Install_score()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p /www/server/panel/plugin/score
	wget -O /www/server/panel/plugin/score/score_main.py $download_Url/install/lib/plugin/score/score_main.py -T 5
	sleep 0.1;
	wget -O /www/server/panel/plugin/score/index.html $download_Url/install/lib/plugin/score/index.html -T 5
	sleep 0.1;
	wget -O /www/server/panel/plugin/score/testcpu.c $download_Url/install/lib/plugin/score/testcpu.c -T 5
	gcc /www/server/panel/plugin/score/testcpu.c -o /www/server/panel/plugin/score/testcpu -lpthread
	if [ ! -f '/www/server/panel/plugin/score/testcpu' ];then
		sleep 0.1
		gcc /www/server/panel/plugin/score/testcpu.c -o /www/server/panel/plugin/score/testcpu -lpthread
	fi
	
	
	if [ ! -f '/www/server/panel/static/img/soft_ico/ico-score.png' ];then
		wget -O /www/server/panel/static/img/soft_ico/ico-score.png $download_Url/install/lib/plugin/score/img/ico-score.png
	fi
	
	wget -O /www/server/panel/plugin/score/info.json $download_Url/install/lib/plugin/score/info.json -T 5
	echo '安装完成' > $install_tmp
}

Uninstall_score()
{
	rm -rf /www/server/panel/plugin/score
	echo '卸载完成' > $install_tmp
}


action=$1
if [ "${1}" == 'install' ];then
	Install_score
else
	Uninstall_score
fi
