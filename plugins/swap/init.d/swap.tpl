#!/bin/bash
# chkconfig: 2345 55 25
# description: MW Cloud Service

### BEGIN INIT INFO
# Provides:          bt
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts mw
# Description:       starts the mw
### END INIT INFO


PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

app_file={$SERVER_PATH}

app_start(){
	isStart=`free -m|grep Swap|awk '{print $2}'`
	if [ "$isStart" == '0' ];then
        echo -e "Starting swap... \c"
        swapon $app_file
        echo -e "\033[32mdone\033[0m"
    else
        echo "Starting swap already running"
    fi
}

app_stop()
{
    echo -e "Stopping swap... \c";
    swapoff $app_file
    echo -e "\033[32mdone\033[0m"
}

app_status()
{
    isStart=`free -m|grep Swap|awk '{print $2}'`
    if [ "$isStart" == '0' ];then
        echo -e "\033[32mswap already running\033[0m"
    else
        echo -e "\033[31mswap not running\033[0m"
    fi
}

case "$1" in
    'start') app_start;;
    'stop') app_stop;;
    'restart'|'reload') 
        app_stop
        app_start;;
    'status') app_status;;
esac