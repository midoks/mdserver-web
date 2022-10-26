#!/bin/bash
#
# chkconfig: 2345 85 15
# description: Pure-FTPd is an FTP server daemon based upon Troll-FTPd
# processname: pure-ftpd

### BEGIN INIT INFO
# Provides:          pureftpd
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts pureftpd server
# Description:       starts pureftpd server
### END INIT INFO

# Pure-FTPd Settings
PURE_PERL="{$SERVER_PATH}/pureftp/sbin/pure-config.pl"
PURE_CONF="{$SERVER_PATH}/pureftp/etc/pure-ftpd.conf"
PURE_PID="{$SERVER_PATH}/pureftp/etc/pure-ftpd.pid"
RETVAL=0
prog="Pure-FTPd"

start() {
    echo -n $"Starting $prog... "
    $PURE_PERL $PURE_CONF --daemonize
    if [ "$?" = 0 ] ; then
        echo " done"
    else
        echo " failed"
    fi
}

stop() {
    echo -n $"Stopping $prog...  "
    if [ ! -e $PURE_PID ]; then
        echo -n $"$prog is not running."
        exit 1
    fi
    kill `cat $PURE_PID`
    if [ "$?" = 0 ] ; then
        echo " done"
    else
        echo " failed"
    fi
}

restart(){
    echo $"Restarting $prog..."
    $0 stop
    sleep 2
    $0 start
}

status(){
    if [ -e $PURE_PID ]; then
        echo $"$prog is running."
    else
        echo $"$prog is not running."
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart}"
esac
