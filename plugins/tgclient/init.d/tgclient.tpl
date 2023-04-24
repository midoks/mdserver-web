#!/bin/sh
# chkconfig: 2345 55 25
# description: Tgbot Service

### BEGIN INIT INFO
# Provides:          Tgbot
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts Tgbot
# Description:       starts the MDW-Web
### END INIT INFO

# Simple Tgbot init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

PATH=/usr/local/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export LANG=en_US.UTF-8


mw_path={$SERVER_PATH}
PATH=$PATH:$mw_path/bin

if [ -f $mw_path/bin/activate ];then
    source $mw_path/bin/activate
fi

tg_start(){	

	isStart=`ps -ef|grep 'tgclient.py' |grep -v grep | awk '{print $2}'`
    if [ "$isStart" == '' ];then
        echo -e "starting tgclient... \c"
        cd $mw_path
        echo "python3 {$APP_PATH}/tgclient.py"
        python3 {$APP_PATH}/tgclient.py >> {$APP_PATH}/task.log &
        isStart=""
        while [[ "$isStart" == "" ]];
        do
            echo -e ".\c"
            sleep 0.5
            isStart=`ps -ef|grep 'tgclient.py' |grep -v grep | awk '{print $2}'`
            let n+=1
            if [ $n -gt 20 ];then
                break;
            fi
        done
        if [ "$isStart" == '' ];then
            echo -e "\033[31mfailed\033[0m"
            echo -e "\033[31mError: tgclient service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo "starting tgclient...(pid $(echo $isStart)) already running"
    fi
}


tg_stop(){
	echo -e "stopping tgclient ... \c";
    arr=`ps aux|grep 'tgclient.py'|grep -v grep|awk '{print $2}'`
    for p in ${arr[@]}
    do
        kill -9 $p > /dev/null 2>&1
    done
    echo -e "\033[32mdone\033[0m"
}

case "$1" in
    start)
		tg_start
        ;;
    stop)
        tg_stop
        ;;
	restart|reload)
		tg_stop
		sleep 0.3
		tg_start
		;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

