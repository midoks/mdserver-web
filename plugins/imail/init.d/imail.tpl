#!/bin/sh
#
#       /etc/rc.d/init.d/imail
#
#       Runs the imail
#       
#
# chkconfig:   - 85 15 
#

### BEGIN INIT INFO
# Provides:          imail
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Should-Start:      mysql
# Should-Stop:       mysql
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start imail at boot time.
# Description:       Control imail.
### END INIT INFO

# Source function library.
if [ -f /etc/init.d/functions ];then
  . /etc/init.d/functions
fi

if [ -f /etc/rc.d/init.d/functions ];then
  . /etc/rc.d/init.d/functions
fi

# Default values
export HOME={$HOME_DIR}
export USER={$RUN_USER}
NAME=imail
GOGS_HOME={$SERVER_PATH}/imail
GOGS_PATH=${GOGS_HOME}/$NAME
GOGS_USER={$RUN_USER}
SERVICENAME="imail"
LOCKFILE=/tmp/imail.lock
LOGPATH=${GOGS_HOME}/log
LOGFILE=${LOGPATH}/imail.log
RETVAL=0


[ -r /etc/sysconfig/$NAME ] && . /etc/sysconfig/$NAME
DAEMON_OPTS="--check $NAME"
[ ! -z "$GOGS_USER" ] && DAEMON_OPTS="$DAEMON_OPTS --user=${GOGS_USER}"


status(){
  isStart=`ps -ef|grep 'imail web' |grep -v grep|awk '{print $2}'`
  if [ "$isStart" == '' ];then
      echo -e "${SERVICENAME} not running"
  else
      echo -e "${SERVICENAME}(pid $(echo $isStart)) already running"
  fi
}

start() {
    isStart=`ps -ef|grep 'imail web' |grep -v grep|awk '{print $2}'`
    if [ "$isStart" != '' ];then
        echo "${SERVICENAME}(pid $(echo $isStart)) already running"
        return $RETVAL
    fi

    cd ${GOGS_HOME}
    echo -e "Starting ${SERVICENAME}: \c"
    ${GOGS_PATH} web > ${LOGFILE} 2>&1 &
    RETVAL=$?
    [ $RETVAL = 0 ] && touch ${LOCKFILE} && echo -e "\033[32mdone\033[0m"
    return $RETVAL
}

stop() {

    pids=`ps -ef|grep 'gogs web' |grep -v grep|awk '{print $2}'`
    arr=($pids)
    echo -e "Stopping gogs... \c"
    for p in ${arr[@]}
    do
            kill -9 $p
    done
    echo -e "\033[32mdone\033[0m"
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
