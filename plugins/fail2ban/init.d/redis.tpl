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

CONF="{$SERVER_PATH}/redis/redis.conf"
REDISPORT=$(cat $CONF |grep port|grep -v '#'|awk '{print $2}')
REDISPASS=$(cat $CONF |grep requirepass|grep -v '#'|awk '{print $2}')
if [ "$REDISPASS" != "" ];then
	REDISPASS=" -a $REDISPASS"
fi
EXEC={$SERVER_PATH}/redis/bin/redis-server
CLIEXEC="{$SERVER_PATH}/redis/bin/redis-cli -p $REDISPORT$REDISPASS"
PIDFILE={$SERVER_PATH}/redis/redis.pid

echo $REDISPASS
echo $REDISPORT
echo $CLIEXEC

mkdir -p {$SERVER_PATH}/redis/data

redis_start(){
	if [ -f $PIDFILE ];then
		kill -9 `cat $PIDFILE`
	fi
	
	echo "Starting Redis server..."
	nohup $EXEC $CONF >> {$SERVER_PATH}/redis/logs.pl 2>&1 &
}
redis_stop(){
	if [ ! -f $PIDFILE ]
	then
		echo "$PIDFILE does not exist, process is not running"
	else
		PID=$(cat $PIDFILE)
		echo "Stopping ..."
		$CLIEXEC shutdown save 2>/dev/null
		while [ -x /proc/${PID} ]
		do
			echo "Waiting for Redis to shutdown ..."
			sleep 1
		done
		echo "Redis stopped"
		rm -rf $PIDFILE
	fi
}


case "$1" in
    start)
		redis_start
        ;;
    stop)
        redis_stop
        ;;
	restart|reload)
		redis_stop
		sleep 0.3
		redis_start
		;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

