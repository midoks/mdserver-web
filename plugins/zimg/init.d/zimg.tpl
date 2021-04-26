#!/bin/sh
# chkconfig: 2345 55 25
# description: zimg Service

### BEGIN INIT INFO
# Provides:          zimg
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts zimg
# Description:       starts the MDW-Web
### END INIT INFO


app_start(){
	# aria2c -D
	cd {$SERVER_PATH}/zimg/bin
	./zimg -d {$SERVER_PATH}/zimg/bin/conf/zimg.lua </dev/null &>/dev/null
	echo "zimg started"
}
app_stop(){
	echo "Stopping ..."
	arr=`ps -ef | grep "zimg" | grep -v 'grep' | grep -v '/bin/sh'|grep -v 'index.py' | awk '{print $2}'`
	echo $arr
	for p in ${arr[@]}
    do
		kill -9 $p &>/dev/null
    done
	echo "zimg stopped"
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

