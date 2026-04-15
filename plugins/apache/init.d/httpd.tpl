#!/bin/bash
# chkconfig: 345 85 15
# description: Apache Server

### BEGIN INIT INFO
# Provides:          apache
# Required-Start:    $network
# Required-Stop:     $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       Apache Server
### END INIT INFO


PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/homebrew/bin
# Apache 可执行文件的路径
DAEMON={$SERVER_PATH}/apache/httpd/bin/httpd
# 进程的 PID 文件路径
PIDFILE={$SERVER_PATH}/apache/httpd/logs/httpd.pid

# 根据传入的参数执行不同操作
case "$1" in
    start)
        echo "Starting Apache..."
        $DAEMON -k start
        ;;
    stop)
        echo "Stopping Apache..."
        $DAEMON -k stop
        ;;
    restart)
        echo "Restarting Apache..."
        $DAEMON -k restart
        ;;
    status)
        if [ -f $PIDFILE ]; then
            echo "Apache is running."
        else
            echo "Apache is not running."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac

exit 0