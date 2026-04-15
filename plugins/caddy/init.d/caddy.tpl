#!/bin/sh
#
#       /etc/rc.d/init.d/caddy
#
#       Runs the caddy
#       
#
# chkconfig:   - 85 15 
#

### BEGIN INIT INFO
# Provides:          caddy
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Should-Start:      caddy
# Should-Stop:       caddy
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start caddy at boot time.
# Description:       Control caddy.
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
NAME=caddy
CADDY_HOME={$SERVER_PATH}/caddy
CADDY_PATH=${CADDY_HOME}/bin/$NAME
CADDY_USER={$RUN_USER}
SERVICENAME="caddy"
LOCKFILE=/tmp/caddy.lock
LOGPATH=${CADDY_HOME}/log
LOGFILE=${LOGPATH}/caddy.log
RETVAL=0

if [ -d $LOGPATH ];then
    mkdir -p $LOGPATH
fi

[ -r /etc/sysconfig/$NAME ] && . /etc/sysconfig/$NAME
DAEMON_OPTS="--check $NAME"
[ ! -z "$CADDY_USER" ] && DAEMON_OPTS="$DAEMON_OPTS --user=${CADDY_USER}"

status(){
  isStart=`ps -ef|grep 'caddy run' |grep -v grep|awk '{print $2}'`
  if [ "$isStart" == '' ];then
      echo -e "${SERVICENAME} not running"
  else
      echo -e "${SERVICENAME}(pid $(echo $isStart)) already running"
  fi
}

start() {
    isStart=`ps -ef | grep 'caddy run' | grep -v grep | awk '{print $2}'`
    if [ "$isStart" != '' ];then
        echo "${SERVICENAME}(pid $(echo $isStart)) already running"
        return $RETVAL
    fi

    cd ${CADDY_HOME}
    echo -e "starting ${SERVICENAME}: \c"
    ${CADDY_PATH} run --environ --config ${CADDY_HOME}/Caddyfile > ${LOGFILE} 2>&1 &
    RETVAL=$?
    [ $RETVAL = 0 ] && touch ${LOCKFILE} && echo -e "\033[32mdone\033[0m"
    return $RETVAL
}

stop() {
    pids=`ps -ef | grep 'caddy run' | grep -v grep | awk '{print $2}'`
    arr=($pids)
    echo -e "stopping caddy... \c"
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
