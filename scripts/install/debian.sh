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

# if [ ! -f /www/server/mdserver-web/bin/activate ];then
#     cd /www/server/mdserver-web && python3 -m venv .
# fi

if [ -f /www/server/mdserver-web/bin/activate ];then
	pip install --upgrade pip
    pip install --upgrade setuptools
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate && pip3 install -r /www/server/mdserver-web/requirements.txt
else
    cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt
fi

if [ ! -f /usr/local/bin/pip3 ];then
    python3 -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple
fi


pip3 install gunicorn==20.1.0
pip3 install gevent==21.1.2
pip3 install gevent-websocket==0.10.1
pip3 install requests==2.20.0
pip3 install flask-caching==1.10.1
pip3 install flask-socketio==5.2.0
pip3 install pymongo
pip3 install psutil


cd /www/server/mdserver-web && ./cli.sh start
sleep 5


echo -e "stop mw"
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`

port=7200
if [ -f /www/server/mdserver-web/data/port.pl ];then
    port=$(cat /www/server/mdserver-web/data/port.pl)
fi

n=0
while [[ "$isStart" != "" ]];
do
    echo -e ".\c"
    sleep 0.5
    isStart=$(lsof -n -P -i:$port|grep LISTEN|grep -v grep|awk '{print $2}'|xargs)
    let n+=1
    if [ $n -gt 15 ];then
        break;
    fi
done


echo -e "start mw"
cd /www/server/mdserver-web && sh cli.sh start
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
n=0
while [[ ! -f /etc/init.d/mw ]];
do
    echo -e ".\c"
    sleep 0.5
    let n+=1
    if [ $n -gt 15 ];then
        break;
    fi
done
echo -e "start mw success"

systemctl daemon-reload
cd /www/server/mdserver-web && ./scripts/init.d/mw default
