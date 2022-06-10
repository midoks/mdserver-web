#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8



mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/wwwlogs
mkdir -p /www/backup/database
mkdir -p /www/backup/site


apt install -y wget curl vixie-cron lsof iptables

if [ ! -f /root/.acme.sh ];then	
	curl  https://get.acme.sh | sh
fi


if [ -f /etc/init.d/iptables ];then

	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 888 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 7200 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 3306 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 30000:40000 -j ACCEPT
	service iptables save

	iptables_status=`service iptables status | grep 'not running'`
	if [ "${iptables_status}" == '' ];then
		service iptables restart
	fi
fi


if [ "${isVersion}" == '' ];then
	if [ ! -f "/etc/init.d/iptables" ];then
		yum install firewalld -y
		systemctl enable firewalld
		systemctl start firewalld

		firewall-cmd --permanent --zone=public --add-port=22/tcp
		firewall-cmd --permanent --zone=public --add-port=80/tcp
		firewall-cmd --permanent --zone=public --add-port=443/tcp
		firewall-cmd --permanent --zone=public --add-port=888/tcp
		firewall-cmd --permanent --zone=public --add-port=7200/tcp
		firewall-cmd --permanent --zone=public --add-port=3306/tcp
		firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp
		firewall-cmd --reload
	fi
fi


#安装时不开启
service iptables stop


# apt install -y libevent libevent-devel mysql-devel libjpeg* libpng* gd* zip unzip libmcrypt libmcrypt-devel
apt install unzip


if [ ! -d /www/server/mdserver-web ];then
	wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
	cd /tmp && unzip /tmp/master.zip
	mv /tmp/mdserver-web-master /www/server/mdserver-web
	rm -rf /tmp/master.zip
	rm -rf /tmp/mdserver-web-master
fi 

apt install python3-pip

if [ ! -f /usr/local/bin/pip3 ];then
    python3 -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple
fi


cd /www/server/mdserver-web/scripts && ./lib.sh
chmod 755 /www/server/mdserver-web/data


if [ -f /www/server/mdserver-web/bin/activate ];then
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate && pip3 install -r /www/server/mdserver-web/requirements.txt
else
    cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt
fi

cd /www/server/mdserver-web && ./cli.sh start
sleep 5

cd /www/server/mdserver-web && ./cli.sh stop
cd /www/server/mdserver-web && ./scripts/init.d/mw default
cd /www/server/mdserver-web && ./cli.sh start




