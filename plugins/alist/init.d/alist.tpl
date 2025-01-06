#!/bin/sh
# chkconfig: 2345 55 25
# description: alist Service

### BEGIN INIT INFO
# Provides:          alist
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts alist
# Description:       starts the MDW-Web
### END INIT INFO

# Simple alist init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

app_start(){
	echo "Starting alist server..."
	cd {$SERVER_PATH}/alist
	./alist server >> {$SERVER_PATH}/alist/logs.pl 2>&1 &
}

app_stop(){
	echo "dztasks stopped"
	ps -ef| grep alist | grep -v grep | grep -v python | grep -v sh | awk '{print $2}'| xargs kill -9
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

