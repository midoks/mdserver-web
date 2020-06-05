#!/bin/sh
# chkconfig: 2345 55 25
# description: shadowsocks Service

### BEGIN INIT INFO
# Provides:          shadowsocks
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts shadowsocks
# Description:       starts the shadowsocks
### END INIT INFO

ROOT_PATH={$SERVER_PATH}

p_start(){
	isStart=$(ps -ef | grep shadowsocks | grep -v grep | grep -v 'init.d' | grep -v 'service' | awk '{print $2}')
    if [ "$isStart" == "" ];then
        echo -e "Starting shadowsocks... \c"
        

        ssserver -c $ROOT_PATH/shadowsocks/shadowsocks.json -d start
        sleep 0.3
        isStart=$(ps -ef | grep shadowsocks  | grep -v grep  | grep -v 'init.d' | grep -v 'service' | awk '{print $2}')
        if [ "$isStart" == '' ];then
                echo -e "\033[31mError: shadowsocks service startup failed.\033[0m"
                return;
        fi

        echo -e "\033[32mdone\033[0m"
    else
		echo "Starting shadowsocks(pid $isStart) already running"
    fi
}

p_stop(){
	echo -e "Stopping shadowsocks... \c";
    pids=$(ps -ef | grep shadowsocks  | grep -v grep | grep -v 'init.d' | grep -v 'service' | awk '{print $2}')
    arr=($pids)

    for p in ${arr[@]}
    do
            kill -9 $p
    done
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

