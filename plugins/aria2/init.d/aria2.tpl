#!/bin/sh
# chkconfig: 2345 55 25
# description: aria2 Service

### BEGIN INIT INFO
# Provides:          aria2
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts aria2
# Description:       starts the MDW-Web
### END INIT INFO


app_start(){
	# aria2c -D
	aria2c --daemon --enable-rpc --rpc-listen-all -c -D --conf-path={$SERVER_PATH}/aria2/aria2/aria2.conf
	echo "aria2 started"
}
app_stop(){
	echo "Stopping ..."
	arr=`ps -ef | grep "aria2" | grep -v 'grep' | grep -v '/bin/sh'|grep -v 'index.py' | awk '{print $2}'`
	echo $arr
	for p in ${arr[@]}
    do
		kill -9 $p &>/dev/null
    done
	echo "aria2 stopped"
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

