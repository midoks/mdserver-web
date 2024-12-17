#!/bin/sh
# chkconfig: 2345 55 25
# description: Redis Service

### BEGIN INIT INFO
# Provides:          Redis
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts Redis
# Description:       starts the MDW-Web
### END INIT INFO

# Simple Redis init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

CONF="{$SERVER_PATH}/valkey/valkey.conf"
REDISPORT=$(cat $CONF |grep port|grep -v '#'|awk '{print $2}')
REDISPASS=$(cat $CONF |grep requirepass|grep -v '#'|awk '{print $2}')
if [ "$REDISPASS" != "" ];then
	REDISPASS=" -a $REDISPASS"
fi
EXEC={$SERVER_PATH}/valkey/bin/valkey-server
CLIEXEC="{$SERVER_PATH}/valkey/bin/valkey-cli -p $REDISPORT$REDISPASS"
PIDFILE={$SERVER_PATH}/valkey/valkey.pid

echo $REDISPASS
echo $REDISPORT
echo $CLIEXEC

mkdir -p {$SERVER_PATH}/valkey/data

valkey_start(){
	if [ -f $PIDFILE ];then
		kill -9 `cat $PIDFILE`
	fi
	
	echo "Starting valkey server..."
	nohup $EXEC $CONF >> {$SERVER_PATH}/valkey/logs.pl 2>&1 &
}

valkey_stop(){
	if [ ! -f $PIDFILE ]
	then
		echo "$PIDFILE does not exist, process is not running"
	else
		PID=$(cat $PIDFILE)
		echo "Stopping ..."
		$CLIEXEC shutdown save 2>/dev/null
		while [ -x /proc/${PID} ]
		do
			echo "Waiting for valkey to shutdown ..."
			sleep 1
		done
		echo "valkey stopped"
		rm -rf $PIDFILE
	fi
}


case "$1" in
    start)
		valkey_start
        ;;
    stop)
        valkey_stop
        ;;
	restart|reload)
		valkey_stop
		sleep 0.3
		valkey_start
		;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

