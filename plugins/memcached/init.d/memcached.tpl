#! /bin/bash
#
# memcached:    MemCached Daemon   
#
# chkconfig:    - 90 25  
# description:  MemCached Daemon   
#
### BEGIN INIT INFO
# Provides:          memcached
# Required-Start:    $syslog
# Required-Stop:     $syslog
# Should-Start:        $local_fs
# Should-Stop:        $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description:    memcached - Memory caching daemon
# Description:        memcached - Memory caching daemon
### END INIT INFO

IP=127.0.0.1
PORT=11211
USER=root
MAXCONN=1024
CACHESIZE=64
OPTIONS=""

RETVAL=0
prog="memcached"

MEM_PATH={$SERVER_PATH}/memcached

start () {
    echo -n $"Starting $prog: "
    $MEM_PATH/bin/memcached -d -l $IP -p $PORT -u $USER -m $CACHESIZE -c $MAXCONN -P $MEM_PATH/memcached.pid $OPTIONS
    if [ "$?" != 0 ] ; then
        echo " failed"
        exit 1
    else
        echo " done"
    fi
}
stop () {
    echo -n $"Stopping $prog: "
    if [ ! -e $MEM_PATH/$prog.pid ]; then
        echo -n $"$prog is not running."
        exit 1
    fi
    kill `cat $MEM_PATH/memcached.pid`
    if [ "$?" != 0 ] ; then
        echo " failed"
        exit 1
    else
        rm -f ${MEM_PATH}/memcached.pid
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
    *)
        echo $"Usage: $0 {start|stop|status|restart|reload}"
        exit 1
        ;;
esac

exit $?
