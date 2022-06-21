#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8


apt update -y

apt install -y wget curl lsof unzip
apt install -y python3-pip
apt install -y python3-venv

apt install -y cron

if [ ! -d /root/.acme.sh ];then	
	curl  https://get.acme.sh | sh
fi


if [ -f /usr/sbin/ufw ];then

	ufw allow 22/tcp
	ufw allow 80/tcp
	ufw allow 443/tcp
	ufw allow 888/tcp
	ufw allow 7200/tcp
	ufw allow 3306/tcp
	# ufw allow 30000:40000/tcp

fi


if [ -f /usr/sbin/ufw ];then
	ufw disable
fi

if [ ! -f /usr/sbin/ufw ];then
	apt install -y firewalld
	systemctl enable firewalld
	systemctl start firewalld

	firewall-cmd --permanent --zone=public --add-port=22/tcp
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=888/tcp
	firewall-cmd --permanent --zone=public --add-port=7200/tcp
	firewall-cmd --permanent --zone=public --add-port=3306/tcp
	# firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp

	# fix:debian10 firewalld faq
	# https://kawsing.gitbook.io/opensystem/andoid-shou-ji/untitled/fang-huo-qiang#debian-10-firewalld-0.6.3-error-commandfailed-usrsbinip6tablesrestorewn-failed-ip6tablesrestore-v1.8
	sed -i 's#IndividualCalls=no#IndividualCalls=yes#g' /etc/firewalld/firewalld.conf

	firewall-cmd --reload
fi

#安装时不开启
systemctl stop firewalld


cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data


if [ ! -f /usr/local/bin/pip3 ];then
    python3 -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple
fi

# cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt
# pip install --upgrade pip
# pip install --upgrade setuptools
# pip3 install gunicorn==20.1.0
# pip3 install gevent==21.1.2
# pip3 install gevent-websocket==0.10.1
# pip3 install requests==2.20.0
# pip3 install flask-caching==1.10.1
# pip3 install flask-socketio==5.2.0
# pip3 install flask-session==0.3.2
# pip3 install pymongo
# pip3 install psutil


# if [ ! -f /www/server/mdserver-web/bin/activate ];then
#     cd /www/server/mdserver-web && python3 -m venv .
# fi

if [ -f /www/server/mdserver-web/bin/activate ];then
	python -m pip install --upgrade pip
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate && pip3 install -r /www/server/mdserver-web/requirements.txt
else
    cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt
fi

pip3 install gunicorn==20.1.0
pip3 install gevent==20.9.0
pip3 install gevent-websocket==0.10.1
pip3 install requests==2.20.0
pip3 install flask-caching==1.10.1
#ubuntu 20 need
pip3 install flask-socketio==5.2.0
pip3 install flask-session==0.3.2
pip3 install pymongo
pip3 install psutil


cd /www/server/mdserver-web && ./cli.sh start
sleep 5

cd /www/server/mdserver-web && ./cli.sh stop
cd /www/server/mdserver-web && ./scripts/init.d/mw default
cd /www/server/mdserver-web && ./cli.sh start

systemctl daemon-reload
