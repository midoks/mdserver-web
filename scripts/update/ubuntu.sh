#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH
export LANG=en_US.UTF-8
export DEBIAN_FRONTEND=noninteractive

# localedef -v -c -i en_US -f UTF-8 en_US.UTF-8

if grep -Eq "Ubuntu" /etc/*-release; then
    sudo ln -sf /bin/bash /bin/sh
    #sudo dpkg-reconfigure dash
fi


cd /www/server/mdserver-web/scripts && bash lib.sh
chmod 755 /www/server/mdserver-web/data


if [ -f /etc/rc.d/init.d/mw ];then
    bash /etc/rc.d/init.d/mw stop && rm -rf /www/server/mdserver-web/scripts/init.d/mw && rm -rf /etc/rc.d/init.d/mw
fi

echo -e "stop mw"
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
port=7200

if [ -f /www/server/mdserver-web/data/port.pl ];then
    port=$(cat /www/server/mdserver-web/data/port.pl)
fi
n=0
while [[ "$isStart" != "" ]];
do
    echo -e ".\c"
    sleep 0.5
    isStart=$(lsof -n -P -i:$port|grep LISTEN|grep -v grep|awk '{print $2}'|xargs)
    let n+=1
    if [ $n -gt 15 ];then
        break;
    fi
done


echo -e "start mw"
cd /www/server/mdserver-web && bash cli.sh start
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
n=0
while [[ ! -f /etc/rc.d/init.d/mw ]];
do
    echo -e ".\c"
    sleep 1
    let n+=1
    if [ $n -gt 20 ];then
        echo -e "start mw fail"
        exit 1
    fi
done
echo -e "start mw success"

systemctl daemon-reload
