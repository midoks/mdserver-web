#!/bin/bash
# chkconfig: 2345 55 25
# description: Walle Service

### BEGIN INIT INFO
# Provides:          bt
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts walle
# Description:       starts the walle
### END INIT INFO


PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

app_path={$SERVER_PATH}/walle/code


walle_start(){
    isStart=`ps aux | grep 'waller.py'| grep -v grep | awk '{print $2}'`
    if [ "$isStart" == '' ];then
        echo -e "Starting walle... \c"
        cd $app_path && python waller.py  >> $app_path/logs/walle.log 2>&1 &
        sleep 0.3
        isStart=`ps aux | grep 'waller.py' | grep -v grep | awk '{print $2}'`
        sleep 0.2
        if [ "$isStart" == '' ];then
                echo -e "\033[31mfailed\033[0m"
                echo '------------------------------------------------------'
                tail -n 20 $app_path/logs/walle.log
                echo '------------------------------------------------------'
                echo -e "\033[31mError: walle service startup failed.\033[0m"
                return
        fi
        echo -e "\033[32mdone\033[0m"
	else
        echo "Starting ... walle (pid $isStart) already running"
    fi
}


walle_stop()
{
	echo -e "Stopping walle... \c";
    pids=$(ps aux | grep 'waller.py'|grep -v grep|awk '{print $2}')
    arr=($pids)

    for p in ${arr[@]}
    do
            kill -9 $p
    done
    echo -e "\033[32mdone\033[0m"

    echo -e "Stopping walle... \c";
    arr=`ps aux | grep 'waller.py' | grep -v grep | awk '{print $2}'`
	for p in ${arr[@]}
    do
            kill -9 $p &>/dev/null
    done
    
    if [ -f $pidfile ];then
    	rm -f $pidfile
    fi
    echo -e "\033[32mdone\033[0m"
}



walle_reload()
{
	isStart=$(ps aux | grep 'waller.py' | grep -v grep | awk '{print $2}')
    
    if [ "$isStart" != '' ];then
    	echo -e "Reload walle... \c";
	    arr=`ps aux|grep 'waller.py' |grep -v grep|awk '{print $2}'`
		for p in ${arr[@]}
        do
                kill -9 $p
        done
        cd $app_path && nohup python waller.py >> $app_path/logs/walle.log 2>&1 &
        isStart=`ps aux | grep 'waller.py' | grep -v grep | awk '{print $2}'`
        if [ "$isStart" == '' ];then
                echo -e "\033[31mfailed\033[0m"
                echo '------------------------------------------------------'
                tail -n 20 $app_path/logs/walle.log
                echo '------------------------------------------------------'
                echo -e "\033[31mError: walle service startup failed.\033[0m"
                return
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo -e "\033[31m walle not running\033[0m"
        mw_start
    fi
}


error_logs()
{
	tail -n 100 ${app_path}/logs/walle.log
}

case "$1" in
    'start') walle_start;;
    'stop') walle_stop;;
    'reload') walle_reload;;
    'restart') 
        walle_stop
        walle_start;;
    'logs') error_logs;;
esac

