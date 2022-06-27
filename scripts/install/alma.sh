#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=C.UTF-8



setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

dnf install -y wget lsof
dnf install -y python3-devel
dnf install -y python-devel
dnf install -y crontabs

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
	yum install firewalld -y
	systemctl enable firewalld
	systemctl start firewalld

	firewall-cmd --permanent --zone=public --add-port=22/tcp
	firewall-cmd --permanent --zone=public --add-port=80/tcp
	firewall-cmd --permanent --zone=public --add-port=443/tcp
	firewall-cmd --permanent --zone=public --add-port=888/tcp
	firewall-cmd --permanent --zone=public --add-port=7200/tcp
	# firewall-cmd --permanent --zone=public --add-port=3306/tcp
	# firewall-cmd --permanent --zone=public --add-port=30000-40000/tcp


	sed -i 's#AllowZoneDrifting=yes#AllowZoneDrifting=no#g' /etc/firewalld/firewalld.conf
	firewall-cmd --reload
fi


#安装时不开启
systemctl stop firewalld

dnf upgrade -y
dnf autoremove -y

dnf groupinstall -y "Development Tools"
dnf install -y epel-release

dnf install -y oniguruma
dnf --enablerepo=crb install oniguruma-devel

dnf install -y libevent libevent-devel libjpeg* libpng* gd* libxslt* unzip libmcrypt libmcrypt-devel
dnf install -y wget libicu-devel zip bzip2-devel gcc libxml2 libxml2-devel libjpeg-devel libpng-devel libwebp libwebp-devel pcre pcre-devel
dnf install -y lsof net-tools
dnf install -y ncurses-devel cmake
dnf --enablerepo=crb install mysql-devel


cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data


cd /www/server/mdserver-web && ./cli.sh start
sleep 5

cd /www/server/mdserver-web && ./cli.sh stop
cd /www/server/mdserver-web && ./scripts/init.d/mw default
cd /www/server/mdserver-web && ./cli.sh start