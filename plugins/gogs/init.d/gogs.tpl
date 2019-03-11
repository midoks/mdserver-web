#!/bin/sh
#
#       /etc/rc.d/init.d/gogs
#
#       Runs the Gogs
#       
#
# chkconfig:   - 85 15 
#

### BEGIN INIT INFO
# Provides:          gogs
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Should-Start:      mysql postgresql
# Should-Stop:       mysql postgresql
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start gogs at boot time.
# Description:       Control gogs.
### END INIT INFO

# Source function library.
if [ -f /etc/init.d/functions ];then
  . /etc/init.d/functions
fi

# Default values
HOME={$HOME_DIR}
NAME=gogs
GOGS_HOME={$SERVER_PATH}/gogs
GOGS_PATH=${GOGS_HOME}/$NAME
GOGS_USER={$RUN_USER}
SERVICENAME="Gogs"
LOCKFILE=/tmp/gogs.lock
LOGPATH=${GOGS_HOME}/log
LOGFILE=${LOGPATH}/gogs.log
RETVAL=0


status(){
  isStart=`ps -ef|grep 'gogs web' |grep -v grep|awk '{print $2}'`
  if [ "$isStart" == '' ];then
      echo "${SERVICENAME} not running"
  else
      echo "${SERVICENAME}(pid $(echo $isStart)) already running"
  fi
}

start() {
    isStart=`ps -ef|grep 'gogs web' |grep -v grep|awk '{print $2}'`
    if [ "$isStart" != '' ];then
        echo "${SERVICENAME}(pid $(echo $isStart)) already running"
        return $RETVAL
    fi

    cd ${GOGS_HOME}
    echo "Starting ${SERVICENAME}: \c"
    ${GOGS_PATH} web > ${LOGFILE} 2>&1 &
    RETVAL=$?
    [ $RETVAL = 0 ] && touch ${LOCKFILE} && echo "\033[32mdone\033[0m"
    return $RETVAL
}

stop() {
    cd ${GOGS_HOME}
    echo "Shutting down ${SERVICENAME}: \c"
    which killproc > /dev/null
    if [ $? -eq 0 ];then
        killproc ${NAME}
    else
        pkill ${NAME}
    fi
    RETVAL=$?
    [ $RETVAL = 0 ] && rm -f ${LOCKFILE}  && echo "\033[32mdone\033[0m"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        start
        ;;
    reload)
        stop
        start
        ;;
    *)
        echo "Usage: ${NAME} {start|stop|status|restart}"
        exit 1
        ;;
esac
exit $RETVAL
