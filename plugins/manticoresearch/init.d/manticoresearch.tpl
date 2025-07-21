#! /bin/bash
#
# searchd:   sphinx Daemon   
#
# chkconfig:    - 90 25  
# description:  sphinx Daemon   
#
### BEGIN INIT INFO
# Provides:          sphinx
# Required-Start:    $syslog
# Required-Stop:     $syslog
# Should-Start:        $local_fs
# Should-Stop:        $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description:    sphinx - Document Index Daemon
# Description:        sphinx - Document Index Daemon
### END INIT INFO

APP_PATH={$SERVER_APP}
APP_CONF={$SERVER_APP}/sphinx.conf
prog="sphinx"

start () {
    echo -n $"Starting $prog: "
    ${APP_PATH}/bin/bin/searchd -c ${APP_CONF}
    if [ "$?" != 0 ] ; then
        echo " failed"
        exit 1
    else
        echo " done"
    fi
}

rebuild () {
    ${APP_PATH}/bin/bin/indexer -c ${APP_CONF} --all --rotate
}


stop () {
    echo -n $"Stopping $prog: "
    if [ ! -e ${APP_PATH}/index/searchd.pid ]; then
        echo -n $"$prog is not running."
        exit 1
    fi
    kill `cat ${APP_PATH}/index/searchd.pid`
    if [ "$?" != 0 ] ; then
        echo " failed"
        exit 1
    else
        rm -f ${APP_PATH}/index/searchd.pid
        echo " done"
    fi
}

restart () {
    $0 stop
    sleep 2
    $0 start
}

# See how we were called.
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart|reload)
        restart
        ;;
    rebuild)
        rebuild
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart|reload}"
        exit 1
        ;;
esac

exit $?