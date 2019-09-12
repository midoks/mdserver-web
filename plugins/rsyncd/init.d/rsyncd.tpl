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
# Description:       starts the rsyncd
### END INIT INFO

ROOT_PATH={$SERVER_PATH}

p_start(){
	isStart=$(ps -ef | grep rsync | grep 'daemon' | grep -v grep | grep -v python | awk '{print $2}')
    if [ "$isStart" == '' ];then
        echo -e "Starting rsync... \c"
        if [ -f /var/run/rsyncd.pid ]; then
			rm -rf /var/run/rsyncd.pid
		fi
        /usr/bin/rsync --daemon --config=/etc/rsyncd.conf
        sleep 0.3
        isStart=$(ps -ef | grep rsync | grep 'daemon' | grep -v grep | grep -v python | awk '{print $2}')
        if [ "$isStart" == '' ];then
                echo -e "\033[31mError: rsyncd service startup failed.\033[0m"
                return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
		echo "Starting rsyncd(pid $isStart) already running"
    fi
}

p_stop(){
	echo -e "Stopping rsyncd... \c";
    pids=$(ps -ef | grep rsync | grep 'daemon' | grep -v grep | grep -v python | awk '{print $2}')
    arr=($pids)

    for p in ${arr[@]}
    do
            kill -9 $p
    done

    if [ -f /var/run/rsyncd.pid ]; then
		rm -rf /var/run/rsyncd.pid
	fi
    echo -e "\033[32mdone\033[0m"
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

