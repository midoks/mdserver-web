#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

mw_path={$SERVER_PATH}

mw_start(){
	isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
	if [ "$isStart" == '' ];then
            echo -e "Starting mw... \c"
            cd $mw_path && gunicorn -c setting.py app:app &
            sleep 0.1
            port=$(cat ${mw_path}/data/port.pl)
            isStart=$(lsof -i :$port|grep LISTEN)
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
            echo "Starting mw... mw(pid $(echo $isStart)) already running"
    fi


    isStart=$(ps aux |grep 'task.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
            echo -e "Starting mw-tasks... \c"
            nohup python task.py >> $mw_path/logs/task.log 2>&1 &
            sleep 0.2
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
            echo "Starting mw-tasks... Bt-Tasks (pid $isStart) already running"
    fi
}




case "$1" in
    'start')
        mw_start
        ;;
esac