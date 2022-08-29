#!/bin/sh
# 
# chkconfig: - 85 15
# description: HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited \
#              for high availability environments.
# processname: haproxy
# config: /etc/haproxy/haproxy.cfg
# pidfile: /var/run/haproxy.pid
# Script Author: Simon Matter <simon.matter@invoca.ch>
# Version: 2004060600
# Source function library.
 
if [ -f /etc/init.d/functions ]; then
  . /etc/init.d/functions
elif [ -f /etc/rc.d/init.d/functions ] ; then
  . /etc/rc.d/init.d/functions
else
  echo ".."
fi
 
# Source networking configuration.
if [ -f /etc/sysconfig/network ];then
  . /etc/sysconfig/network
fi

# Check that networking is up.
# [ ${NETWORKING} = "no" ] && exit 0

HAPROXYDIR={$SERVER_PATH}/haproxy
BASENAME=haproxy
 
# This is our service name
 
#BASENAME=`basename $0`
#if [ -L $0 ]; then
#  BASENAME=`find $0 -name $BASENAME -printf %l`
#  BASENAME=`basename $BASENAME`
#fi
 
[ -f $HAPROXYDIR/etc/$BASENAME.conf ] || exit 1
 
RETVAL=0
 
start() {
    $HAPROXYDIR/sbin/$BASENAME -c -q -f $HAPROXYDIR/etc/$BASENAME.conf


    if [ $? -ne 0 ]; then
    echo "Errors found in configuration file, check it with '$BASENAME check'."
    return 1
    fi

    echo -n "Starting $BASENAME: "
    daemon $HAPROXYDIR/sbin/$BASENAME -D -f $HAPROXYDIR/etc/$BASENAME.conf
    RETVAL=$?
    # echo
    # [ $RETVAL -eq 0 ] && touch /var/lock/subsys/$BASENAME
    return $RETVAL
}
 
 
stop() {
 
  echo -n "Shutting down $BASENAME: "
  killproc $BASENAME -USR1

  RETVAL=$?
  echo
  [ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/$BASENAME
  [ $RETVAL -eq 0 ] && rm -f /var/run/$BASENAME.pid
  return $RETVAL
}
 
restart() {
  $HAPROXYDIR/sbin/$BASENAME -c -q -f $HAPROXYDIR/etc/$BASENAME.conf
  if [ $? -ne 0 ]; then
    echo "Errors found in configuration file, check it with '$BASENAME check'."
    return 1
  fi
  stop
  start
}
 
reload() {
  $HAPROXYDIR/sbin/$BASENAME -c -q -f $HAPROXYDIR/etc/$BASENAME.conf
  if [ $? -ne 0 ]; then
    echo "Errors found in configuration file, check it with '$BASENAME check'."
    return 1
  fi
  $HAPROXYDIR/sbin/$BASENAME -D -f $HAPROXYDIR/$BASENAME.conf -p /var/run/$BASENAME.pid -sf $(cat /var/run/$BASENAME.pid)
}
 
check() {
  $HAPROXYDIR/sbin/$BASENAME -c -q -V -f $HAPROXYDIR/etc/$BASENAME.conf
}
 
rhstatus() {
  status $BASENAME
}
 
condrestart() {
  [ -e /var/lock/subsys/$BASENAME ] && restart || :
}
 
# See how we were called.
case "$1" in
  start) start ;;
  stop) stop ;;
  restart) restart;;
  reload) reload;;
  condrestart) condrestart ;;
  status) rhstatus ;;
  check) check ;;
  *)
    echo $"Usage: $BASENAME {start|stop|restart|reload|condrestart|status|check}"
    exit 1
esac
 
exit $?