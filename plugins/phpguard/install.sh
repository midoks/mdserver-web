#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'
download_Url=http://download.bt.cn

Install_phpguard()
{
	mkdir -p /www/server/panel/plugin/phpguard
	wget -O /www/server/panel/plugin/phpguard/info.json $download_Url/install/lib/plugin/phpguard/info.json -T 5
	echo 'True' > /www/server/panel/data/502Task.pl
}

Uninstall_phpguard()
{
	rm -rf /www/server/panel/plugin/phpguard
	rm -f /www/server/panel/data/502Task.pl
}


action=$1
if [ "${1}" == 'install' ];then
	Install_phpguard
else
	Uninstall_phpguard
fi
