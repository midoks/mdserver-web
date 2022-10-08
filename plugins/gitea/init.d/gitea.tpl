#!/bin/sh
#
#       /etc/rc.d/init.d/Gitea
#
#       Runs the Gogs
#       
#
# chkconfig:   - 85 15 
#

### BEGIN INIT INFO
# Provides:          Gitea
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Should-Start:      mysql postgresql
# Should-Stop:       mysql postgresql
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start Gitea at boot time.
# Description:       Control Gitea.
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
NAME=gitea
GOGS_HOME={$SERVER_PATH}/gitea
GOGS_PATH=${GOGS_HOME}/$NAME
GOGS_USER={$RUN_USER}
SERVICENAME="gitea"
LOCKFILE=/tmp/gitea.lock
LOGPATH=${GOGS_HOME}/log
LOGFILE=${LOGPATH}/gitea.log
RETVAL=0


[ -r /etc/sysconfig/$NAME ] && . /etc/sysconfig/$NAME
DAEMON_OPTS="--check $NAME"
[ ! -z "$GOGS_USER" ] && DAEMON_OPTS="$DAEMON_OPTS --user=${GOGS_USER}"


status(){
  isStart=`ps -ef|grep 'gitea web' |grep -v grep|awk '{print $2}'`
  if [ "$isStart" == '' ];then
      echo -e "${SERVICENAME} not running"
  else
      echo -e "${SERVICENAME}(pid $(echo $isStart)) already running"
  fi
}

start() {
    isStart=`ps -ef|grep 'gitea web' |grep -v grep|awk '{print $2}'`
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

    pids=`ps -ef|grep 'gitea web' |grep -v grep|awk '{print $2}'`
    arr=($pids)
    echo -e "Stopping gitea... \c"
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
