#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/wwwlogs
mkdir -p /www/backup/database
mkdir -p /www/backup/site


yum -y provides '*/applydeltarpm'
yum -y install deltarpm

yum install -y wget curl unzip zip


wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
cd /tmp && unzip /tmp/master.zip
mv /tmp/mdserver-web-master /www/server/mdserver-web
rm -rf /tmp/master.zip
rm -rf /tmp/mdserver-web-master

yum groupinstall -y "Development Tools"
paces="wget python-devel python-imaging zip unzip openssl openssl-devel gcc libxml2 libxml2-dev libxslt* zlib zlib-devel libjpeg-devel libpng-devel libwebp libwebp-devel freetype freetype-devel lsof pcre pcre-devel vixie-cron crontabs"
yum -y install $paces
yum -y lsof net-tools.x86_64
yum -y install ncurses-devel mysql-dev locate
yum -y install epel-release python-devel

if [ ! -f '/usr/bin/pip' ];then
	wget https://bootstrap.pypa.io/get-pip.py
	python get-pip.py
	pip install --upgrade pip
fi 


pip install -r /www/server/mdserver-web/requirements.txt