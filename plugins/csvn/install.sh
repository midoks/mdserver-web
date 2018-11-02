#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH





install_tmp='/tmp/bt_install.pl'

echo "Install_csvn"

#sleep 100
wget -O csvn.tar.xz https://github.com/midoks/mdserver-web/releases/download/init/CollabNetSubversionEdge-5.1.4_linux-x86_64.tar.xz
#useradd csvn

Install_csvn()
{

	echo "ddd"
	# mkdir -p /www/server/panel/plugin/safelogin
	# echo '正在安装脚本文件...' > $install_tmp
	# wget -O /www/server/panel/plugin/safelogin/safelogin_main.py $download_Url/install/lib/plugin/safelogin/safelogin_main.py -T 5
	# wget -O /www/server/panel/plugin/safelogin/index.html $download_Url/install/lib/plugin/safelogin/index.html -T 5
	# wget -O /www/server/panel/plugin/safelogin/info.json $download_Url/install/lib/plugin/safelogin/info.json -T 5
	# wget -O /www/server/panel/plugin/safelogin/icon.png $download_Url/install/lib/plugin/safelogin/icon.png -T 5
	# echo '安装完成' > $install_tmp
	
}

Uninstall_csvn()
{
	echo "Uninstall_csvn"
	# chattr -i /www/server/panel/plugin/safelogin/token.pl
	# rm -f /www/server/panel/data/limitip.conf
	# sed -i "/ALL/d" /etc/hosts.deny
	# rm -rf /www/server/panel/plugin/safelogin
}


# action=$1
# host=$2;
# if [ "${1}" == 'install' ];then
# 	Install_safelogin
# else
# 	Uninstall_safelogin
# fi
