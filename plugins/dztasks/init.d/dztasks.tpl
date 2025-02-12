#!/bin/sh
# chkconfig: 2345 55 25
# description: dztasks Service

### BEGIN INIT INFO
# Provides:          dztasks
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts dztasks
# Description:       starts the MDW-Web
### END INIT INFO

# Simple dztasks init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
PLAIN='\033[0m'
BOLD='\033[1m'
SUCCESS='[\033[32mOK\033[0m]'
COMPLETE='[\033[32mDONE\033[0m]'
WARN='[\033[33mWARN\033[0m]'
ERROR='[\033[31mERROR\033[0m]'
WORKING='[\033[34m*\033[0m]'

app_start(){
    echo "Starting dztasks server..."
    cd {$SERVER_PATH}/dztasks
    ./dztasks web >> {$SERVER_PATH}/dztasks/logs.pl 2>&1 &
}

app_stop(){
    echo "dztasks stopp start"
    pids=`ps -ef| grep dztasks | grep -v grep | grep -v python | grep -v sh | awk '{print $2}'`
    arr=($pids)
    for p in ${arr[@]}
    do
        kill -9 $p  > /dev/null 2>&1
    done
    echo "dztasks stopp end"
}


case "$1" in
    start)
        app_start
        ;;
    stop)
        app_stop
        ;;
    restart|reload)
        app_stop
        sleep 0.3
        app_start
        ;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

