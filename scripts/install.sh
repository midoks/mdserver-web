#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
# LANG=en_US.UTF-8
is64bit=`getconf LONG_BIT`

if [ -f /etc/motd ];then
    echo "welcome to mdserver-web panel" > /etc/motd
fi

startTime=`date +%s`

_os=`uname`
echo "use system: ${_os}"

if [ "$EUID" -ne 0 ]
  then echo "Please run as root!"
  exit
fi

if grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	ln -sf /bin/bash /bin/sh
	#sudo dpkg-reconfigure dash
fi

if grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	ln -sf /bin/bash /bin/sh
fi


if [ ${_os} == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
	yum install -y wget zip unzip
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
	yum install -y wget zip unzip
elif grep -Eqi "Rocky" /etc/issue || grep -Eq "Rocky" /etc/*-release; then
	OSNAME='rocky'
	yum install -y wget zip unzip
elif grep -Eqi "AlmaLinux" /etc/issue || grep -Eq "AlmaLinux" /etc/*-release; then
	OSNAME='alma'
	yum install -y wget zip unzip
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
	apt update -y
	apt install -y devscripts
	apt install -y wget zip unzip
	apt install -y wget zip unzip
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
	apt install -y wget zip unzip
elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
	OSNAME='raspbian'
else
	OSNAME='unknow'
fi


if [ $OSNAME != "macos" ];then
	mkdir -p /www/server
	mkdir -p /www/wwwroot
	mkdir -p /www/wwwlogs
	mkdir -p /www/backup/database
	mkdir -p /www/backup/site

	if [ ! -d /www/server/mdserver-web ];then
		wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
		cd /tmp && unzip /tmp/master.zip
		mv /tmp/mdserver-web-master /www/server/mdserver-web
		rm -rf /tmp/master.zip
		rm -rf /tmp/mdserver-web-master
	fi
fi

echo "use system version: ${OSNAME}"
cd /www/server/mdserver-web && bash scripts/install/${OSNAME}.sh

chmod +x /www/server/mdserver-web/mw-cli
if [ ! -e /usr/bin/mw-cli ]; then 
	ln -s /www/server/mdserver-web/mw-cli /usr/bin/mw-cli
fi
endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"
