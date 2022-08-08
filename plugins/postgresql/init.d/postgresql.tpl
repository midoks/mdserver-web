#!/bin/bash
# chkconfig: 2345 55 25
# description: PostgreSQL Service

### BEGIN INIT INFO
# Provides:          Midoks
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts PostgreSQL
# Description:       starts the PostgreSQL
### END INIT INFO


PATH=/usr/local/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export LC_ALL="en_US.UTF-8"

MW_PATH={$SERVER_PATH}
PATH=$PATH:$MW_PATH/bin

if [ -f $MW_PATH/bin/activate ];then
    source $MW_PATH/bin/activate
fi

pg_start()
{
    touch {$APP_PATH}/logs/server.log
    {$APP_PATH}/bin/pg_ctl -D {$APP_PATH}/data -l {$APP_PATH}/logs/server.log start
}


pg_stop()
{
    {$APP_PATH}/bin/pg_ctl -D {$APP_PATH}/data -l {$APP_PATH}/logs/server.log stop
}


pg_status()
{
    isStart=$(ps aux | grep 'postgres'| grep -v grep | grep -v 'postgresql status' | awk '{print $2}')
    if [ "$isStart" != '' ];then
        echo -e "\033[32mPostgreSQL (pid $isStart) already running\033[0m"
    else
        echo -e "\033[31mPostgreSQL not running\033[0m"
    fi
}


pg_reload()
{
    echo '' > {$APP_PATH}/logs/server.log
	{$APP_PATH}/bin/pg_ctl -D {$APP_PATH}/data -l {$APP_PATH}/logs/server.log reload
}



case "$1" in
    'start') pg_start;;
    'stop') pg_stop;;
    'reload') pg_reload;;
    'restart') 
        pg_stop
        pg_start;;
    'status') 
        pg_status;;
esac
