#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
# LANG=en_US.UTF-8
is64bit=`getconf LONG_BIT`

echo -e "您正在安装的是\033[31m mdserver-web 测试版\033[0m，非开发测试用途请使用正式版 install.sh ！" 
echo -e "\nYou are installing\033[31m mdserver-web dev version \033[0m, normally use install.sh for production.\n" 
sleep 8

{

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


# macOS
if [ ${_os} == "Darwin" ]; then
	OSNAME='macos'
# SUSE Linux
elif grep -Eq "openSUSE" /etc/*-release; then
	OSNAME='opensuse'
	zypper refresh
	zypper install cron wget curl zip unzip
# FreeBSD
elif grep -Eq "FreeBSD" /etc/*-release; then
	OSNAME='freebsd'
# Arch Linux
elif [ -f /etc/arch-release ]; then
	OSNAME='arch'
	pacman -Syu --noconfirm
	pacman -S --noconfirm curl cronie
# Enterprise Linux
elif [ -f /etc/redhat-release ]; then
	if grep -Eq "AlmaLinux" /etc/redhat-release ; then OSNAME='alma';
	elif grep -Eq "CentOS" /etc/redhat-release ; then OSNAME='centos';
	elif grep -Eq "Rocky" /etc/redhat-release ; then OSNAME='rocky';
	elif grep -Eq "Red Hat" /etc/redhat-release ; then OSNAME='rhel';
	fi
	OSNAME='rhel'
	if grep -Eq "Amazon Linux" /etc/redhat-release ; then OSNAME='amazon'; fi
	if grep -Eq "Fedora" /etc/redhat-release ; then OSNAME='fedora'; fi
	yum install -y wget curl zip unzip tar crontabs
# Debian / Ubuntu
elif [ -f /etc/lsb-release ]; then
	OSNAME='debian'
	if grep -Eq "Ubuntu" /etc/os-release; then OSNAME='ubuntu';
	elif grep -Eq "Debian" /etc/os-release; then OSNAME='debian';
	fi
	apt update -y
	apt install -y wget curl zip unzip tar cron
# Others
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
		curl -sSLo /tmp/dev.zip https://github.com/midoks/mdserver-web/archive/refs/heads/dev.zip
		cd /tmp && unzip /tmp/dev.zip
		mv -f /tmp/mdserver-web-dev /www/server/mdserver-web
		rm -rf /tmp/dev.zip
		rm -rf /tmp/mdserver-web-dev
	fi
fi

echo "use system version: ${OSNAME}"
cd /www/server/mdserver-web && bash scripts/install/${OSNAME}.sh

cd /www/server/mdserver-web && bash cli.sh start
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
n=0
while [ ! -f /etc/rc.d/init.d/mw ];
do
    echo -e ".\c"
    sleep 1
    let n+=1
    if [ $n -gt 20 ];then
    	echo -e "start mw fail"
        exit 1
    fi
done

cd /www/server/mdserver-web && bash /etc/rc.d/init.d/mw stop
cd /www/server/mdserver-web && bash /etc/rc.d/init.d/mw start
cd /www/server/mdserver-web && bash /etc/rc.d/init.d/mw default

sleep 2
if [ ! -e /usr/bin/mw ]; then
	if [ -f /etc/rc.d/init.d/mw ];then
		ln -s /etc/rc.d/init.d/mw /usr/bin/mw
	fi
fi

endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"

} 1> >(tee mw-install.log) 2>&1

echo -e "\nInstall completed. If error occurs, please contact us with the log file mw-install.log ."
echo "安装完毕，如果出现错误，请带上同目录下的安装日志 mw-install.log 联系我们反馈."