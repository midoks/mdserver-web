#!/bin/sh
# chkconfig: 2345 55 25
# description: Mongodb Service

### BEGIN INIT INFO
# Provides:          Mongodb
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts Mongodb
# Description:       starts the MDW-Web
### END INIT INFO

# Simple Mongodb init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

CONF="{$SERVER_PATH}/mongodb/mongodb.conf"
EXEC={$SERVER_PATH}/mongodb/bin/mongod

PIDFILE={$SERVER_PATH}/mongodb/mongodb.pid

mkdir -p {$SERVER_PATH}/mongodb/data
mkdir -p {$SERVER_PATH}/mongodb/logs

app_start(){
	if [ -f $PIDFILE ];then
		kill -9 `cat $PIDFILE`
	fi
	
	echo "Starting mongodb server..."
	echo $EXEC -f $CONF
	$EXEC -f $CONF >> {$SERVER_PATH}/mongodb/logs.pl 1>&1 2>&1 &
}

app_stop(){
	if [ ! -f $PIDFILE ]
	then
			echo "$PIDFILE does not exist, process is not running"
	else
			PID=$(cat $PIDFILE)
			echo "Stopping ..."
			kill -9 $PID
			while [ -x /proc/${PID} ]
			do
				echo "Waiting for mongodb to shutdown ..."
				sleep 1
			done
			echo "mongodb stopped"
			rm -rf $PIDFILE
	fi
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

