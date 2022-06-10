#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8



wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
rm -rf /tmp/mdserver-web-master
cd /tmp && unzip  /tmp/master.zip
cp -rf /tmp/mdserver-web-master/* /www/server/mdserver-web
rm -rf /tmp/master.zip
rm -rf /tmp/mdserver-web-master


cd /www/server/mdserver-web/scripts && sh lib.sh

chmod 755 /www/server/mdserver-web/data

#venv
cd /www/server/mdserver-web && python3 -m venv .

if [ ! -f /usr/local/bin/pip3 ];then
    python3 -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple
fi

if [ -f /www/server/mdserver-web/bin/activate ];then
    cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate && pip3 install -r /www/server/mdserver-web/requirements.txt
else

    cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt
fi

pip3 install gevent flask gunicorn flask_caching flask_session
pip3 install flask_socketio gevent-websocket

sh /etc/init.d/mw stop && rm -rf  /www/server/mdserver-web/scripts/init.d/mw && rm -rf  /etc/init.d/mw

echo -e "stop mw"
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
port=$(cat /www/server/mdserver-web/data/port.pl)
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
cd /www/server/mdserver-web && sh cli.sh start
isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
n=0
while [[ ! -f /etc/init.d/mw ]];
do
    echo -e ".\c"
    sleep 0.5
    let n+=1
    if [ $n -gt 15 ];then
        break;
    fi
done
echo -e "start mw success"

/etc/init.d/mw default


