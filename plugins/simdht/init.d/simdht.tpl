#!/bin/sh
# chkconfig: 2345 55 25
# description: DHTSpider Service

### BEGIN INIT INFO
# Provides:          DHTSpider
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts DHTSpider
# Description:       starts the MDW-Web
### END INIT INFO


dht_start(){
	cd {$SERVER_PATH}/simdht/workers
	nohup python simdht_worker.py > {$SERVER_PATH}/simdht/logs.pl 2>&1 &
	echo "simdht started"
}
dht_stop(){
	echo "Stopping ..."
	ps -ef | grep "python simdht" | grep -v grep | awk '{print $2}' | xargs kill
	echo "simdht stopped"
}


case "$1" in
    start)
		dht_start
        ;;
    stop)
        dht_stop
        ;;
	restart|reload)
		dht_stop
		sleep 0.3
		dht_start
		;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

