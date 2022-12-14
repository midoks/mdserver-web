#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
# LANG=en_US.UTF-8
is64bit=`getconf LONG_BIT`

startTime=`date +%s`

_os=`uname`
echo "use system: ${_os}"

if [ "$EUID" -ne 0 ]
  then echo "Please run as root!"
  exit
fi

if [ ${_os} != "Darwin" ] && [ ! -d /www/server/mdserver-web/logs ]; then
	mkdir -p /www/server/mdserver-web/logs
fi

{
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


cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ];then
	curl -sSLo /tmp/master.zip https://gitee.com/midoks/mdserver-web/repository/archive/master.zip
else
	curl -sSLo /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
fi


cd /tmp && unzip /tmp/master.zip
/usr/bin/cp -rf  /tmp/mdserver-web-master/* /www/server/mdserver-web
rm -rf /tmp/master.zip
rm -rf /tmp/mdserver-web-master


if [ -f /etc/rc.d/init.d/mw ];then
    sh /etc/rc.d/init.d/mw stop && rm -rf /www/server/mdserver-web/scripts/init.d/mw && rm -rf /etc/rc.d/init.d/mw
fi

#pip uninstall public
echo "use system version: ${OSNAME}"
cd /www/server/mdserver-web && bash scripts/update/${OSNAME}.sh

bash /etc/rc.d/init.d/mw restart
bash /etc/rc.d/init.d/mw default

if [ -f /usr/bin/mw ];then
	rm -rf /usr/bin/mw
fi

if [ ! -e /usr/bin/mw ]; then
	if [ ! -f /usr/bin/mw ];then
		ln -s /etc/rc.d/init.d/mw /usr/bin/mw
	fi
fi

endTime=`date +%s`
((outTime=($endTime-$startTime)/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"

} 1> >(tee /www/server/mdserver-web/logs/mw-update.log) 2>&1