#!/bin/bash
# chkconfig: 2345 55 25
# description: Nezha Agent Service

### BEGIN INIT INFO
# Provides:          Nezha Agent
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts Nezha Agent
# Description:       starts the Nezha Agent
### END INIT INFO

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

if [ -f /etc/init.d/functions ];then
  . /etc/init.d/functions
fi

if [ -f /etc/rc.d/init.d/functions ];then
  . /etc/rc.d/init.d/functions
fi

SERVICENAME=nezha-agent
LOG_PATH={$SERVER_PATH}/nezha/logs
APP_PATH={$SERVER_PATH}/nezha/agent
APP_HOST={$APP_HOST}
APP_SECRET={$APP_SECRET}


app_start(){
    isStart=`ps -ef|grep "${SERVICENAME}" | grep -v grep | grep -v python | grep -v "/bin/bash" | awk '{print $2}'`
    if [ "$isStart" == '' ];then
        echo -e "Starting ${SERVICENAME}... \c"
        cd $APP_PATH
        exec nohup ${APP_PATH}/${SERVICENAME} -d -s ${APP_HOST} -p ${APP_SECRET} >> ${LOG_PATH}/${SERVICENAME}.log 2>&1 &
        isStart=""
        while [[ "$isStart" == "" ]];
        do
            echo -e ".\c"
            sleep 0.5
            isStart=$(ps -ef|grep "${SERVICENAME}" |grep -v grep | grep -v python | grep -v "/bin/bash" | awk '{print $2}')
            let n+=1
            if [ $n -gt 15 ];then
                break;
            fi
        done
        if [ "$isStart" == '' ];then
            echo -e "\033[31mError: ${SERVICENAME} service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo "Starting ${SERVICENAME}(pid $(echo $isStart)) already running"
    fi
}

app_stop(){
    pids=`ps -ef | grep "${SERVICENAME}" | grep -v grep | grep -v python | grep -v "/bin/bash" |awk '{print $2}'`
    arr=($pids)
    echo -e "Stopping ${SERVICENAME}... \c"
    for p in ${arr[@]}
    do
        # echo "$p"
        kill -9 $p
    done
    echo -e "\033[32mdone\033[0m"
}

app_status(){
    isStart=`ps -ef | grep "${SERVICENAME}" | grep -v grep | grep -v python | grep -v "/bin/bash" | awk '{print $2}'`
    if [ "$isStart" == '' ];then
      echo -e "${SERVICENAME} not running"
    else
      echo -e "${SERVICENAME}(pid $(echo $isStart)) already running"
    fi
}

case "$1" in
    'start') app_start;;
    'stop') app_stop;;
    'status') app_status;;
    'reload') 
        app_stop
        app_start;;
    'restart') 
        app_stop
        app_start;;
esac