#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8
is64bit=`getconf LONG_BIT`

startTime=`date +%s`

_os=`uname`
echo "use system: ${_os}"

if grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	sudo ln -sf /bin/bash /bin/sh
	#sudo dpkg-reconfigure dash
fi

if grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	sudo ln -sf /bin/bash /bin/sh
fi

if [ "${_os}" == "Darwin" ]; then
	OSNAME='macos'
elif grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
	OSNAME='centos'
elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
	OSNAME='fedora'
elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
	OSNAME='debian'
elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
	OSNAME='ubuntu'
elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
	OSNAME='raspbian'
else
	OSNAME='unknow'
fi

#pip uninstall public
echo "use system version: ${OSNAME}"
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/update/${OSNAME}.sh | sh

endTime=`date +%s`
((outTime=($endTime-$startTime)/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"