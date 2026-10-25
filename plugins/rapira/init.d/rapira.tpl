#!/bin/sh
# chkconfig: 2345 55 25
# description: Rapira Service

### BEGIN INIT INFO
# Provides:          Rapira
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts Rapira
# Description:       starts the MDW-Web
### END INIT INFO

# Simple Rapira init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

mkdir -p {$SERVER_PATH}/rapira/data

app_start(){
	echo "Starting Rapira server..."
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{$SERVER_PATH}/rapira/{$VERSION}/link/lib
	export DYLD_FALLBACK_LIBRARY_PATH={$SERVER_PATH}/rapira/{$VERSION}/link/lib
	export PHPRC={$SERVER_PATH}/rapira/{$VERSION}
	{$SERVER_PATH}/rapira/{$VERSION}/bin/rapira serve {$SERVER_PATH}/rapira/{$VERSION}/rapira.toml >> {$SERVER_PATH}/rapira/logs.pl 2>&1 &
}
app_stop(){
	ps -ef|grep "{$VERSION}/rapira.toml"|grep -v grep |awk '{print $2}'| xargs -r kill -9
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

