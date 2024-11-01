#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
DIR=$(cd "$(dirname "$0")"; pwd)
MDIR=$(dirname "$DIR")

export LC_ALL="en_US.UTF-8"

# echo $DIR

PATH=$PATH:$DIR/bin
if [ -f ${DIR}/bin/activate ];then
	source ${DIR}/bin/activate

	if [ "$?" != "0" ];then
		echo "load local python env fail!"
	fi
fi

mw_start_task()
{
    isStart=$(ps aux |grep 'panel_task.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
        echo -e "starting mw-tasks... \c"
        cd $DIR && python3 panel_task.py >> ${DIR}/logs/panel_task.log 2>&1 &
        sleep 0.3
        isStart=$(ps aux |grep 'panel_task.py'|grep -v grep|awk '{print $2}')
        if [ "$isStart" == '' ];then
            echo -e "\033[31mfailed\033[0m"
            echo '------------------------------------------------------'
            tail -n 20 $DIR/logs/panel_task.log
            echo '------------------------------------------------------'
            echo -e "\033[31mError: mw-tasks service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo "starting mw-tasks... mw-tasks (pid $(echo $isStart)) already running"
    fi
}

mw_start(){
	cd web && gunicorn -c setting.py app:app
	#安全启动
	mw_start_task
}


mw_start_debug(){
	if [ ! -f $DIR/logs/panel_task.log ];then
		echo '' > $DIR/logs/panel_task.log
	fi

	python3 panel_task.py >> $DIR/logs/panel_task.log 2>&1 &
	port=7200    
    if [ -f /www/server/mdserver-web/data/port.pl ];then
        port=$(cat /www/server/mdserver-web/data/port.pl)
    fi

    if [ -f ${DIR}/data/port.pl ];then
        port=$(cat ${DIR}/data/port.pl)
    fi
    # gunicorn -b :${port} -k gevent -w 1 app:app
	cd ${DIR}/web && gunicorn -b :${port} -w 1 app:app
}

mw_start_debug2(){
	python3 panel_task.py >> $DIR/logs/panel_task.log 2>&1 &
	cd ${DIR}/web && gunicorn -b :7200 -w 1  app:app
}

mw_start_debug3(){
	cd ${DIR}/web && gunicorn -c setting.py app:app
	cd ${DIR} && python3 panel_task.py
}


mw_stop()
{
	PLIST=`ps -ef|grep app:app |grep -v grep|awk '{print $2}'`
	for i in $PLIST
	do
	    kill -9 $i > /dev/null 2>&1
	done

	pids=`ps -ef|grep panel_task.py | grep -v grep |awk '{print $2}'`
	arr=($pids)
    for p in ${arr[@]}
    do
    	kill -9 $p > /dev/null 2>&1
    done
}

case "$1" in
    'start') mw_start;;
    'stop') mw_stop;;
    'restart') 
		mw_stop 
		mw_start
		;;
	'debug') 
		mw_stop 
		mw_start_debug
		;;
	'debug2') 
		mw_stop 
		mw_start_debug2
		;;
	'debug3') 
		mw_stop 
		mw_start_debug3
		;;
esac