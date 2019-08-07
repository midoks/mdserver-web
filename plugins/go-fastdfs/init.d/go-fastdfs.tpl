#!/bin/bash
# chkconfig: 2345 55 25
# description: go-fastdfs Cloud Service

### BEGIN INIT INFO
# Provides:          bt
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts go-fastdfs
# Description:       starts the go-fastdfs
### END INIT INFO


PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

gf_path={$SERVER_PATH}/go-fastdfs

gf_start(){
isStart=`ps -ef| grep -v python|grep -v bash |grep go-fastdfs |grep -v .jar | grep -v grep|awk '{print $2}'`
if [ "$isStart" == '' ];then
    echo -e "Starting go-fastdfs... \c"
    cd $gf_path
    nohup ./go-fastdfs > /dev/null 2>&1 &
    echo -e "\033[32mdone\033[0m"
else
    echo -e "Starting go-fastdfs(pid $(echo $isStart)) already running"
fi
}


gf_stop()
{
    echo -e "Stopping go-fastdfs... \c"

    pids=$(ps -ef| grep -v python |grep -v bash |grep go-fastdfs |grep -v .jar | grep -v grep | awk '{print $2}')
    arr=($pids)

    for p in ${arr[@]}
    do
        kill -9 $p
    done
    echo -e "\033[32mdone\033[0m"
}

gf_status()
{
    isStart=$(ps -ef | grep -v python | grep -v bash | grep go-fastdfs |grep -v .jar | grep -v grep | awk '{print $2}')
    if [ "$isStart" != '' ];then
        echo -e "\033[32mgo-fastdfs (pid $(echo $isStart)) already running\033[0m"
    else
        echo -e "\033[31mgo-fastdfs not running\033[0m"
    fi
}


gf_reload()
{
    gf_stop
    gf_start
}

case "$1" in
    'start') gf_start;;
    'stop') gf_stop;;
    'reload') gf_reload;;
    'status') gf_status;;
    'restart') 
        gf_stop
        gf_start;;
esac