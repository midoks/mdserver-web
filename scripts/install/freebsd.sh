#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

if grep -Eq "FreeBSD" /etc/*-release && [ ! -f /bin/bash ]; then
    ln -sf /usr/local/bin/bash /bin/bash
fi

echo "y" | pkg update 
pkg install -y python3
# python3 -m ensurepip
# pip3 install --upgrade setuptools
# python3 -m pip install --upgrade pip
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

SSH_PORT=`netstat -ntpl|grep sshd|grep -v grep | sed -n "1,1p" | awk '{print $4}' | awk -F : '{print $2}'`
if [ "$SSH_PORT" == "" ];then
	SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep "Port \d*" | tail -1`
	SSH_PORT=${SSH_PORT_LINE/"Port "/""}
fi
echo "SSH PORT:${SSH_PORT}"

# if [ -f /usr/sbin/iptables ];then

# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
# 	iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 888 -j ACCEPT
# 	service iptables save

# 	iptables_status=`service iptables status | grep 'not running'`
# 	if [ "${iptables_status}" == '' ];then
# 		service iptables restart
# 	fi

# 	#安装时不开启
# 	service iptables stop
# fi

if [ ! -f /usr/sbin/iptables ];then
	pkg install -y firewalld 
	systemctl enable firewalld
	systemctl start firewalld

	if [ "$SSH_PORT" != "" ];then
		firewall-cmd --permanent --zone=public --add-port=${SSH_PORT}/tcp
	else
		firewall-cmd --permanent --zone=public --add-port=22/tcp
	fi

	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=888/tcp


	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	firewall-cmd --reload
	#安装时不开启
	systemctl stop firewalld
fi

cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data

