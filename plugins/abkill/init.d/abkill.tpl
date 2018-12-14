#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

ak_path={$SERVER_PATH}/abkill

ak_start(){
    isStart=$(ps aux |grep 'abkill.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
            echo -e "Starting abkill... \c"
            cd $ak_path && nohup python abkill.py >> $ak_path/task.log 2>&1 &
            sleep 0.3
            isStart=$(ps aux |grep 'abkill.py'|grep -v grep|awk '{print $2}')
            if [ "$isStart" == '' ];then
                    echo -e "\033[31mfailed\033[0m"
                    echo '------------------------------------------------------'
                    tail -n 20 $ak_path/task.log
                    echo '------------------------------------------------------'
                    echo -e "\033[31mError: abkill service startup failed.\033[0m"
                    return;
            fi
            echo -e "\033[32mdone\033[0m"
    else
            echo "Starting abkill(pid $isStart) already running"
    fi
}


ak_stop()
{
	echo -e "Stopping abkill... \c";
    pids=$(ps aux | grep 'abkill.py' | grep -v grep|awk '{print $2}')
    arr=($pids)

    for p in ${arr[@]}
    do
            kill -9 $p
    done
    echo -e "\033[32mdone\033[0m"

}

ak_status()
{
    isStart=$(ps aux|grep 'abkill.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" != '' ];then
            echo -e "\033[32mabkill (pid $(echo $isStart)) already running\033[0m"
    else
            echo -e "\033[31mabkill not running\033[0m"
    fi
}


ak_reload()
{
	isStart=$(ps aux|grep 'abkill.py'|grep -v grep|awk '{print $2}')
    
    if [ "$isStart" != '' ];then
    	ak_stop
        ak_start
    else
        echo -e "\033[31mmw not running\033[0m"
        mw_start
    fi
}


case "$1" in
    'start') ak_start;;
    'stop') ak_stop;;
    'reload') ak_reload;;
    'restart') 
        ak_stop
        sleep 0.3
        ak_start;;
    'status') ak_status;;
esac