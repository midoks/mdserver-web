#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

mw_path={$SERVER_PATH}

mw_start(){
	isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
	if [ "$isStart" == '' ];then
            echo -e "Starting mw... \c"
            cd $mw_path && gunicorn -c setting.py app:app
            sleep 0.6
            port=$(cat ${mw_path}/data/port.pl)
            isStart=$(lsof -i :$port|grep LISTEN)
            if [ "$isStart" == '' ];then
                    echo -e "\033[31mfailed\033[0m"
                    echo '------------------------------------------------------'
                    tail -n 20 ${mw_path}/logs/error.log
                    echo '------------------------------------------------------'
                    echo -e "\033[31mError: mw service startup failed.\033[0m"
                    return;
            fi
            echo -e "\033[32mdone\033[0m"
    else
            echo "Starting mw... mw(pid $(echo $isStart)) already running"
    fi


    isStart=$(ps aux |grep 'task.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
            echo -e "Starting mw-tasks... \c"
            cd $mw_path && nohup python task.py >> $mw_path/logs/task.log 2>&1 &
            sleep 0.3
            isStart=$(ps aux |grep 'task.py'|grep -v grep|awk '{print $2}')
            if [ "$isStart" == '' ];then
                    echo -e "\033[31mfailed\033[0m"
                    echo '------------------------------------------------------'
                    tail -n 20 $mw_path/logs/task.log
                    echo '------------------------------------------------------'
                    echo -e "\033[31mError: mw-tasks service startup failed.\033[0m"
                    return;
            fi
            echo -e "\033[32mdone\033[0m"
    else
            echo "Starting mw-tasks... mw-tasks (pid $isStart) already running"
    fi
}


mw_stop()
{
	echo -e "Stopping mw-tasks... \c";
    pids=$(ps aux | grep 'task.py'|grep -v grep|awk '{print $2}')
    arr=($pids)

    for p in ${arr[@]}
    do
            kill -9 $p
    done
    echo -e "\033[32mdone\033[0m"

    echo -e "Stopping mw... \c";
    arr=`ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}'`
	for p in ${arr[@]}
    do
            kill -9 $p &>/dev/null
    done
    
    if [ -f $pidfile ];then
    	rm -f $pidfile
    fi
    echo -e "\033[32mdone\033[0m"
}

mw_status()
{
        isStart=$(ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}')
        if [ "$isStart" != '' ];then
                echo -e "\033[32mmw (pid $(echo $isStart)) already running\033[0m"
        else
                echo -e "\033[31mmw not running\033[0m"
        fi
        
        isStart=$(ps aux |grep 'task.py'|grep -v grep|awk '{print $2}')
        if [ "$isStart" != '' ];then
                echo -e "\033[32mmw-task (pid $isStart) already running\033[0m"
        else
                echo -e "\033[31mmw-task not running\033[0m"
        fi
}


mw_reload()
{
	isStart=$(ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}')
    
    if [ "$isStart" != '' ];then
    	echo -e "Reload mw... \c";
	    arr=`ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}'`
		for p in ${arr[@]}
        do
                kill -9 $p
        done
        cd $mw_path && gunicorn -c setting.py app:app
        isStart=`ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}'`
        if [ "$isStart" == '' ];then
                echo -e "\033[31mfailed\033[0m"
                echo '------------------------------------------------------'
                tail -n 20 $mw_path/logs/error.log
                echo '------------------------------------------------------'
                echo -e "\033[31mError: mw service startup failed.\033[0m"
                return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo -e "\033[31mmw not running\033[0m"
        mw_start
    fi
}


error_logs()
{
	tail -n 100 $mw_path/logs/error.log
}

case "$1" in
    'start') mw_start;;
    'stop') mw_stop;;
    'reload') mw_reload;;
    'restart') 
        mw_stop
        mw_start;;
    'status') mw_status;;
    'logs') error_logs;;
esac