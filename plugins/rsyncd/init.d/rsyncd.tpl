#!/bin/sh
# chkconfig: 2345 55 25
# description: rsyncd Service

### BEGIN INIT INFO
# Provides:          rsyncd
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts rsyncd
# Description:       starts the MDW-Web
### END INIT INFO

ROOT_PATH={$SERVER_PATH}

p_start(){
	echo "Starting ..."
	cd $ROOT_PATH/rsyncd/init.d
	if [ -f /var/run/rsyncd.pid ]; then
		rm -rf /var/run/rsyncd.pid
	fi
	/usr/bin/rsync --daemon
	echo "rsyncd started"
}

p_stop(){
	echo "Stopping ..."
	ps -ef | grep rsync | grep -v grep | grep -v python | awk '{print $2}' | xargs kill -9
	if [ -f /var/run/rsyncd.pid ]; then
		rm -rf /var/run/rsyncd.pid
	fi
	echo "rsyncd stopped"
}


case "$1" in
    start)
		p_start
        ;;
    stop)
        p_stop
        ;;
	restart|reload)
		p_stop
		sleep 0.3
		p_start
		;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

