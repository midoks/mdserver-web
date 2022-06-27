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
	apt install -y wget zip unzip
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
	apt install -y wget zip unzip
elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
	OSNAME='raspbian'
else
	OSNAME='unknow'
fi

wget -O /tmp/dev.zip https://github.com/midoks/mdserver-web/archive/refs/heads/dev.zip
cd /tmp && unzip /tmp/dev.zip
cp -rf /tmp/mdserver-web-dev/* /www/server/mdserver-web
rm -rf /tmp/dev.zip
rm -rf /tmp/mdserver-web-dev

#pip uninstall public
echo "use system version: ${OSNAME}"

# cd /www/server/mdserver-web && bash ./scripts/install/debian.sh
cd /www/server/mdserver-web && bash scripts/update/${OSNAME}.sh
# curl -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update/${OSNAME}.sh | bash

endTime=`date +%s`
((outTime=($endTime-$startTime)/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"