#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/wwwlogs
mkdir -p /www/backup/database
mkdir -p /www/backup/site


if [ ! -f /usr/bin/applydeltarpm ];then
	yum -y provides '*/applydeltarpm'
	yum -y install deltarpm
fi


setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

yum install -y wget lsof crontabs
yum install -y python3-devel
yum install -y python-devel
yum install -y vixie-cron

#https need

if [ ! -d /root/.acme.sh ];then	
	curl https://get.acme.sh | sh
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

	#安装时不开启
	service iptables stop
fi


if [ ! -f /etc/init.d/iptables ];then
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

sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf

systemctl restart firewalld
#安装时不开启
systemctl stop firewalld

yum groupinstall -y "Development Tools"

yum install -y libevent libevent-devel libjpeg* libpng* gd* libxslt* unzip libmcrypt libmcrypt-devel
yum install -y wget python-imaging libicu-devel zip bzip2-devel gcc libxml2 libxml2-dev  libjpeg-devel libpng-devel libwebp libwebp-devel pcre pcre-devel
yum install -y lsof net-tools
yum install -y ncurses-devel mysql-devel cmake
yum install -y MySQL-python 
yum install -y epel-release

if [ ! -d /www/server/mdserver-web ];then
	wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
	cd /tmp && unzip /tmp/master.zip
	mv /tmp/mdserver-web-master /www/server/mdserver-web
	rm -rf /tmp/master.zip
	rm -rf /tmp/mdserver-web-master
fi

#if [ ! -f '/usr/bin/pip' ];then
#	wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
#	python get-pip.py
#	pip install --upgrade pip
#	pip install pillow==6.2.2
#fi 


if [ ! -f /usr/local/bin/pip3 ];then
    python3 -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple
fi


cd /www/server/mdserver-web/scripts && sh lib.sh

chmod 755 /www/server/mdserver-web/data

if [ -f /www/server/mdserver-web/bin/activate ];then
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate && pip3 install -r /www/server/mdserver-web/requirements.txt
else
    cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt
fi

pip3 install gunicorn==20.1.0
pip3 install gevent==21.1.2
pip3 install gevent-websocket==0.10.1
pip3 install requests==2.20.0
pip3 install flask_socketio psutil pymongo



cd /www/server/mdserver-web && ./cli.sh start
sleep 5

cd /www/server/mdserver-web && ./cli.sh stop
cd /www/server/mdserver-web && ./scripts/init.d/mw default
cd /www/server/mdserver-web && ./cli.sh start