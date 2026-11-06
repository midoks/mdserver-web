#!/bin/sh
# chkconfig: 2345 55 25
# description: manticore Service

### BEGIN INIT INFO
# Provides:          manticore
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts manticore
# Description:       starts the MDW-Web
### END INIT INFO

# Simple manticore init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

app_start(){
	echo "Starting manticore server..."
	# /usr/bin/searchd --config /etc/manticoresearch/manticore.conf
	{$SERVER_APP}/bin/searchd --config {$SERVER_APP}/etc/manticoresearch/manticore.conf >> {$SERVER_APP}/logs.pl 2>&1 &
}
app_stop(){
	ps -ef | grep "manticoresearch/bin/searchd" | grep -v grep |awk '{print $2}'| xargs -r kill -9
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

