#!/bin/bash
# chkconfig: 2345 55 25
# description:system_safe

### BEGIN INIT INFO
# Provides:          system_safe
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts system_safe
# Description:       starts the system_safe
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
mw_path={$SERVER_PATH}
rootPath=$(dirname "$mw_path")
PATH=$PATH:$mw_path/bin

if [ -f $rootPath/mdserver-web/bin/activate ];then
    source $rootPath/mdserver-web/bin/activate
fi

sys_start()
{
    isStart=$(ps aux |grep -E "(system_safe)"|grep -v grep|grep -v '/bin/bash'|grep -v 'system_safe/system_safe.py start' | grep -v 'system_safe/system_safe.py reload' | grep -v 'system_safe/system_safe.py restart' | grep -v systemctl | grep -v '/bin/sh' | awk '{print $2}'|xargs)
    if [ "$isStart" == '' ];then
        echo -e "Starting system_safe service... \c"
        cd $rootPath/mdserver-web
        nohup python3 plugins/system_safe/system_safe.py bg_start &> $mw_path/service.log &
        sleep 0.5
        isStart=$(ps aux |grep -E "(system_safe)"|grep -v grep|awk '{print $2}'|xargs)
        if [ "$isStart" == '' ];then
            echo -e "\033[31mfailed\033[0m"
            echo '------------------------------------------------------'
            cat $mw_path/service.log
            echo '------------------------------------------------------'
            echo -e "\033[31mError: system_safe service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo "Starting system_safe service (pid $isStart) already running"
    fi
}

sys_stop()
{
    echo -e "Stopping system_safe service... \c";
    pids=$(ps aux |grep -E "(system_safe)"|grep -v grep|grep -v '/bin/bash'|grep -v systemctl | grep -v 'system_safe/system_safe.py bg_stop'|grep -v 'system_safe/system_safe.py stop' | grep -v 'system_safe/system_safe.py reload' | grep -v 'system_safe/system_safe.py restart' |awk '{print $2}'|xargs)
    arr=($pids)
    for p in ${arr[@]}
    do
        kill -9 $p
    done
    cd $rootPath/mdserver-web
    python3 plugins/system_safe/system_safe.py bg_stop
    echo -e "\033[32mdone\033[0m"
}

sys_status()
{
    isStart=$(ps aux |grep -E "(system_safe)"|grep -v grep|grep -v systemctl|awk '{print $2}'|xargs)
    if [ "$isStart" != '' ];then
        echo -e "\033[32msystem_safe service (pid $isStart) already running\033[0m"
    else
        echo -e "\033[31msystem_safe service not running\033[0m"
    fi
}

case "$1" in
    'start')
        sys_start
        ;;
    'stop')
        sys_stop
        ;;
    'restart')
        sys_stop
        sleep 0.2
        sys_start
        ;;
    'reload')
        sys_stop
        sleep 0.2
        sys_start
        ;;
    'status')
        sys_status
        ;;
    *)
        echo "Usage: systemctl {start|stop|restart|reload} system_safe"
    ;;
esac