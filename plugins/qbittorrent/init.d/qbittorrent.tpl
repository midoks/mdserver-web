#!/bin/sh
# chkconfig: 2345 55 25
# description: qbittorrent Service

### BEGIN INIT INFO
# Provides:          qbittorrent
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts qbittorrent
# Description:       starts the MDW-Web
### END INIT INFO


qb_start(){
	isStartFF=`ps -ef | grep 'ffmpeg' | grep -v grep |awk '{print $2}'`
	if [ "$isStartFF" != '' ];then
		echo "qbittorrent ffmpeg is running! can\`t start!!!"
		return 1
	fi

	cd {$SERVER_PATH}/qbittorrent/workers
	nohup python qbittorrent_worker.py > {$SERVER_PATH}/qbittorrent/logs.pl  2>&1 &
	echo "qbittorrent started"
}

qb_stop(){
	isStartFF=`ps -ef | grep 'ffmpeg' | grep -v grep |awk '{print $2}'`
	echo `ps -ef | grep 'ffmpeg'`
	if [ "$isStartFF" != '' ];then
		echo "qbittorrent ffmpeg is running! can\`t stop!!!"
		return 1
	fi

	echo "Stopping ..."
	#ps -ef | grep qbittorrent-nox-bin | grep -v grep | awk '{print $2}' | xargs kill -9
	ps -ef | grep "qbittorrent_worker.py" | grep -v grep | awk '{print $2}' | xargs kill -9
	echo "qbittorrent stopped"
}


case "$1" in
    start)
		qb_start
        ;;
    stop)
        qb_stop
        ;;
	restart|reload)
		qb_stop
		sleep 0.3
		qb_start
		;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

