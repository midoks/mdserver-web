#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

if grep -Eq "FreeBSD" /etc/*-release && [ ! -f /bin/bash ]; then
    ln -sf /usr/local/bin/bash /bin/bash
fi

pkg update -y
pkg install -y python3
python3 -m ensurepip
pip3 install --upgrade setuptools
python3 -m pip install --upgrade pip
pkg install -y lsof
pkg install -y sqlite3
pkg install -y py38-sqlite3
pkg install -y py38-mysqlclient
pkg install -y py38-cffi

pkg install -y gcc
pkg install -y autoconf
pkg install -y make 
pkg install -y gmake
pkg install -y cmake
pkg install -y libxslt
pkg install -y libunwind
pkg install -y influxpkg-config
pkg install -y expect

pkg install -y pcre
pkg install -y webp
pkg install -y freetype
pkg install -y oniguruma
pkg install -y brotli
pkg install -y harfbuzz

# pkg install -y py38-cffi


pkg autoremove -y

#https need
if [ ! -d /root/.acme.sh ];then	
	curl https://get.acme.sh | sh
fi

if [ -f /etc/init.d/iptables ];then

	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 888 -j ACCEPT
	# iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 7200 -j ACCEPT
	# iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 3306 -j ACCEPT
	# iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 30000:40000 -j ACCEPT
	service iptables save

	iptables_status=`service iptables status | grep 'not running'`
	if [ "${iptables_status}" == '' ];then
		service iptables restart
	fi

	#安装时不开启
	service iptables stop
fi


if [ ! -f /etc/init.d/iptables ];then
	pkg install -y firewalld 
	systemctl enable firewalld
	systemctl start firewalld

	firewall-cmd --permanent --zone=public --add-port=22/tcp
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=888/tcp
	# firewall-cmd --permanent --zone=public --add-port=7200/tcp
	# firewall-cmd --permanent --zone=public --add-port=3306/tcp
	# firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp


	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	firewall-cmd --reload
	#安装时不开启
	systemctl stop firewalld
fi




cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data


cd /www/server/mdserver-web && bash cli.sh start
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
n=0
while [[ ! -f /etc/init.d/mw ]];
do
    echo -e ".\c"
    sleep 1
    let n+=1
    if [ $n -gt 20 ];then
    	echo -e "start mw fail"
        exit 1
    fi
done

cd /www/server/mdserver-web && bash /etc/init.d/mw stop
cd /www/server/mdserver-web && bash /etc/init.d/mw start
cd /www/server/mdserver-web && bash /etc/init.d/mw default

