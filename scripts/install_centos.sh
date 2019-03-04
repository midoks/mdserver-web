#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/wwwlogs
mkdir -p /www/backup/database
mkdir -p /www/backup/site

wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
cd /tmp && unzip /tmp/master.zip
# mv /tmp/mdserver-web-master /www/server/mdserver-web
# rm -rf /tmp/master.zip
# rm -rf /tmp/mdserver-web-master




pip install -r /www/server/mdserver-web/requirements.txt


cd /www/server/mdserver-web && ./cli.sh start
cd /www/server/mdserver-web && ./cli.sh stop
sleep 5
cd /www/server/mdserver-web && ./scripts/init.d/mw default
cd /www/server/mdserver-web && ./cli.sh start
