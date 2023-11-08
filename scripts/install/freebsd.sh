#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
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
pkg install -y rar
pkg install -y unrar
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
pkg install -y libmemcached
pkg install -y webp
pkg install -y freetype
pkg install -y oniguruma
pkg install -y brotli
pkg install -y harfbuzz
pkg install -y libevent
pkg install -y pidof
pkg install -y pstree

# curl https://sh.rustup.rs -sSf | sh
pkg install -y rust

pkg autoremove -y


SSH_PORT_LINE=`cat /etc/ssh/sshd_config | grep -E "Port d*" | tail -1`
SSH_PORT=${SSH_PORT_LINE/"Port "/""}

echo "SSH PORT:${SSH_PORT}"

# 检测防火墙是否开启
FW_ENABLE=`cat /etc/rc.conf | grep firewall_enable`
if [ "$FW_ENABLE" == "" ];then
	sysrc firewall_enable="YES"
	sysrc firewall_type="open"
	sysrc firewall_script="/etc/ipfw.rules"
	sysrc firewall_logging="YES"
	sysrc firewall_logif="YES"
fi

# ipfw list
service ipfw stop


cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data

