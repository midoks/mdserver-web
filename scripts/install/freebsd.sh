#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

# -- debug start --

# https://www.freebsd.org/where/

# 手动升级到,可解决库找不到的问题。
# freebsd-update -r 13.2-RELEASE upgrade
# freebsd-update -r 14-RELEASE upgrade

# pkg install -y python39
# python3 -m ensurepip
# pip3 install --upgrade setuptools
# python3 -m pip install --upgrade pip

# echo "y" | pkg upgrade

# -- debug end   --

if grep -Eq "FreeBSD" /etc/*-release && [ ! -f /bin/bash ]; then
    ln -sf /usr/local/bin/bash /bin/bash
fi


echo "y" | pkg update
echo "y" | pkg bootstrap -f
echo "y" | freebsd-update install

pkg install -y python3
pkg install -y py39-pip

pkg install -y lsof
pkg install -y vim
pkg install -y sqlite3

pkg install -y py39-sqlite3

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

# curl https://sh.rustup.rs -sSf | sh
pkg install -y rust

pkg autoremove -y


SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep -E "Port d*" | tail -1`
SSH_PORT=${SSH_PORT_LINE/"Port "/""}

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
	# firewall-cmd --list-all
	# iptables -nL --line-number
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

