#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
cd /tmp && unzip /tmp/master.zip
rm -rf  /www/server/mdserver-web/scripts/init.d/mw
rm -rf  /etc/init.d/mw


/usr/bin/cp -rf  /tmp/mdserver-web-master/* /www/server/mdserver-web
rm -rf /tmp/master.zip
rm -rf /tmp/mdserver-web-master

cd /www/server/mdserver-web/scripts && sh lib.sh

pip install -r /www/server/mdserver-web/requirements.txt

cd /www/server/mdserver-web && sh cli.sh start
sleep 5
cd /www/server/mdserver-web && sh cli.sh stop
cd /www/server/mdserver-web && sh scripts/init.d/mw default
cd /www/server/mdserver-web && sh cli.sh start