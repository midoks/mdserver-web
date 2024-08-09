#!/bin/sh
# chkconfig: 2345 55 25
# description: Gorse Service

### BEGIN INIT INFO
# Provides:          Gorse
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts Gorse
# Description:       starts the MDW-Web
### END INIT INFO

# Simple Gorse init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

CONF="{$SERVER_PATH}/gorse/gorse.toml"

APP_DIR={$SERVER_PATH}/gorse

app_start(){
	echo "Starting Gorse server..."
	echo "$APP_DIR/bin/gorse-in-one -c $CONF"
	nohup $APP_DIR/bin/gorse-in-one -c $CONF >> {$SERVER_PATH}/gorse/logs.pl 2>&1 &
}

app_stop(){
	echo "Stopping ..."
	
	find_gorse=`ps -ef | grep gorse | grep -v grep | awk "{print $2}"`
	for p in ${find_gorse[@]}
    do
        kill -9 $p > /dev/null 2>&1
    done

	echo "Gorse stopped"
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

