#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8


mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/wwwlogs
mkdir -p /www/backup/database
mkdir -p /www/backup/site

apt update -y

apt install -y wget curl vixie-cron lsof iptables
apt install -y python3-pip
apt install -y python3-venv

if [ ! -d /root/.acme.sh ];then	
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
		apt install firewalld
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
echo "debian dev..."

