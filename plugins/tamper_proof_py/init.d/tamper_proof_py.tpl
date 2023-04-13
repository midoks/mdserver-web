#!/bin/bash
# chkconfig: 2345 55 25
# description:tamper_proof_service

### BEGIN INIT INFO
# Provides:          tamper_proof_service
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts tamper_proof_service
# Description:       starts the tamper_proof_service
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
mw_path={$SERVER_PATH}
rootPath=$(dirname "$mw_path")
PATH=$PATH:$mw_path/bin

if [ -f $rootPath/mdserver-web/bin/activate ];then
    source $rootPath/mdserver-web/bin/activate
fi

# cd /www/server/mdserver-web && python3 plugins/tamper_proof_py/tamper_proof_service.py start
sys_start()
{
    isStart=$(ps aux |grep -E "(tamper_proof_service)"|grep -v grep |grep -v 'tamper_proof_py/tamper_proof_service.py start' | grep -v 'tamper_proof_py/tamper_proof_service.py reload' | grep -v 'tamper_proof_py/tamper_proof_service.py restart' | grep -v systemctl | grep -v '/bin/sh' | grep -v '/bin/bash' | awk '{print $2}'|xargs)
    if [ "$isStart" == '' ];then
        echo -e "Starting tamper_proof_service... \c"
        cd $rootPath/mdserver-web
        nohup python3 plugins/tamper_proof_py/tamper_proof_service.py start &> $mw_path/service.log &
        sleep 0.5
        isStart=$(ps aux |grep -E "(tamper_proof_service)"|grep -v grep|awk '{print $2}'|xargs)
        if [ "$isStart" == '' ];then
            echo -e "\033[31mfailed\033[0m"
            echo '------------------------------------------------------'
            cat $mw_path/service.log
            echo '------------------------------------------------------'
            echo -e "\033[31mError: tamper_proof_service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo "Starting tamper_proof_service (pid $isStart) already running"
    fi
}

sys_stop()
{
    echo -e "Stopping tamper_proof_service... \c";
    pids=$(ps aux |grep -E "(tamper_proof_service)"|grep -v grep|grep -v '/bin/bash'|grep -v systemctl | grep -v 'tamper_proof_py/tamper_proof_service.py stop' | grep -v 'tamper_proof_py/tamper_proof_service.py reload' | grep -v 'tamper_proof_py/tamper_proof_service.py restart' |awk '{print $2}'|xargs)
    arr=($pids)
    for p in ${arr[@]}
    do
        kill -9 $p
    done
    cd $rootPath/mdserver-web
    python3 plugins/tamper_proof_py/tamper_proof_service.py stop
    echo -e "\033[32mdone\033[0m"
}

sys_status()
{
    isStart=$(ps aux |grep -E "(tamper_proof_service)"|grep -v grep|grep -v "init.d/tamper_proof_py"|grep -v systemctl|awk '{print $2}'|xargs)
    if [ "$isStart" != '' ];then
        echo -e "\033[32mtamper_proof_service (pid $isStart) already running\033[0m"
    else
        echo -e "\033[32mtamper_proof_service not running\033[0m"
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
        echo "Usage: systemctl {start|stop|restart|reload} tamper_proof_service"
    ;;
esac