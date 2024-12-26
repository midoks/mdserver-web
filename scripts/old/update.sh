#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
# LANG=en_US.UTF-8
is64bit=`getconf LONG_BIT`

startTime=`date +%s`

VERSION=0.17.3

_os=`uname`
echo "use system: ${_os}"

if [ "$EUID" -ne 0 ]
  then echo "Please run as root!"
  exit
fi

if [ ${_os} != "Darwin" ] && [ ! -d /www/server/mdserver-web/logs ]; then
	mkdir -p /www/server/mdserver-web/logs
fi

LOG_FILE=/var/log/mw-update.log

{

if [ ${_os} == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eqi "openSUSE" /etc/*-release; then
	OSNAME='opensuse'
	zypper refresh
elif grep -Eqi "EulerOS" /etc/*-release || grep -Eqi "openEuler" /etc/*-release; then
	OSNAME='euler'
elif grep -Eqi "FreeBSD" /etc/*-release; then
	OSNAME='freebsd'
elif grep -Eqi "CentOS" /etc/issue || grep -Eqi "CentOS" /etc/*-release; then
	OSNAME='rhel'
	yum install -y wget zip unzip
elif grep -Eqi "Fedora" /etc/issue || grep -Eqi "Fedora" /etc/*-release; then
	OSNAME='rhel'
	yum install -y wget zip unzip
elif grep -Eqi "Rocky" /etc/issue || grep -Eqi "Rocky" /etc/*-release; then
	OSNAME='rhel'
	yum install -y wget zip unzip
elif grep -Eqi "AlmaLinux" /etc/issue || grep -Eqi "AlmaLinux" /etc/*-release; then
	OSNAME='rhel'
	yum install -y wget zip unzip
elif grep -Eqi "Amazon Linux" /etc/issue || grep -Eqi "Amazon Linux" /etc/*-release; then
	OSNAME='amazon'
	yum install -y wget zip unzip
elif grep -Eqi "Debian" /etc/issue || grep -Eqi "Debian" /etc/*-release; then
	OSNAME='debian'
	apt install -y wget zip unzip
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eqi "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
	apt install -y wget zip unzip
elif grep -Eqi "Raspbian" /etc/issue || grep -Eqi "Raspbian" /etc/*-release; then
	OSNAME='raspbian'
else
	OSNAME='unknow'
fi


HTTP_PREFIX="https://"
LOCAL_ADDR=common
cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
	LOCAL_ADDR=cn
	HTTP_PREFIX="https://mirror.ghproxy.com/"
fi
echo "local:${LOCAL_ADDR}"

CP_CMD=/usr/bin/cp
if [ -f /bin/cp ];then
		CP_CMD=/bin/cp
fi

if [ "$LOCAL_ADDR" != "common" ];then
	# curl --insecure -sSLo /tmp/master.zip https://code.midoks.icu/midoks/mdserver-web/archive/master.zip
	wget --no-check-certificate -O /tmp/master.zip https://github.com/midoks/mdserver-web/archive/refs/tags/${VERSION}.zip
	cd /tmp && unzip /tmp/master.zip

	$CP_CMD -rf /tmp/mdserver-web-${VERSION}/* /www/server/mdserver-web
	rm -rf /tmp/master.zip
	rm -rf /tmp/mdserver-web-${VERSION}

	pip install -r /www/server/mdserver-web/requirements.txt
else
	# curl --insecure -sSLo /tmp/master.zip https://github.com/midoks/mdserver-web/archive/refs/tags/0.17.3.zip
	curl --insecure -sSLo /tmp/master.zip https://github.com/midoks/mdserver-web/archive/refs/tags/${VERSION}.zip

	cd /tmp && unzip /tmp/master.zip
	$CP_CMD -rf /tmp/mdserver-web-${VERSION}/* /www/server/mdserver-web
	rm -rf /tmp/master.zip
	rm -rf /tmp/mdserver-web-${VERSION}

	pip install -r /www/server/mdserver-web/requirements.txt
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

} 1> >(tee $LOG_FILE) 2>&1