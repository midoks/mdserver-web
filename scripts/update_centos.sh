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

isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
port=$(cat data/port.pl)
while [[ "$isStart" == "" ]];
do
    echo -e ".\c"
    sleep 0.5
    isStart=$(lsof -n -P -i:$port|grep LISTEN|grep -v grep|awk '{print $2}'|xargs)
    let n+=1
    if [ $n -gt 8 ];then
        break;
    fi
done

cd /www/server/mdserver-web \
&& sh cli.sh stop \
&& sh cli.sh start \
&& sh scripts/init.d/mw default