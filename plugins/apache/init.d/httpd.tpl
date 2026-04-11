#! /bin/sh
# chkconfig: 2345 55 25
# Description: Startup script for nginx webserver on Debian. Place in /etc/init.d and
# run 'update-rc.d -f nginx defaults', or use the appropriate command on your
# distro. For CentOS/Redhat run: 'chkconfig --add openresty'

### BEGIN INIT INFO
# Provides:          nginx
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the nginx web server
# Description:       starts nginx using start-stop-daemon
### END INIT INFO


PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/homebrew/bin
NAME=nginx
NGINX_BIN={$SERVER_PATH}/openresty/bin/openresty
CONFIGFILE={$SERVER_PATH}/openresty/nginx/conf/$NAME.conf
PIDFILE={$SERVER_PATH}/openresty/nginx/logs/$NAME.pid

case "$1" in
    start)
        echo -n "Starting $NAME... "
		if [ -f $PIDFILE ];then
			mPID=`cat $PIDFILE`
			isStart=`ps ax | awk '{ print $1 }' | grep -e "^${mPID}$"`
			if [ "$isStart" != '' ];then
				echo "$NAME (pid `pidof $NAME`) already running."
				exit 1
			fi
		fi

        $NGINX_BIN -c $CONFIGFILE

        if [ "$?" != 0 ] ; then
            echo " failed"
            exit 1
        else
            echo " done"
        fi
        ;;

    stop)
        echo -n "Stoping $NAME... "
		if [ -f $PIDFILE ];then
			mPID=`cat $PIDFILE`
			isStart=`ps ax | awk '{ print $1 }' | grep -e "^${mPID}$"`
			if [ "$isStart" = '' ];then
				echo "$NAME is not running."
				exit 1
			fi
		else
			echo "$NAME is not running."
			exit 1
        fi
        $NGINX_BIN -s stop

        if [ "$?" != 0 ] ; then
            echo " failed. Use force-quit"
            exit 1
        else
            echo " done"
        fi
        ;;

    status)
		if [ -f $PIDFILE ];then
			mPID=`cat $PIDFILE`
			isStart=`ps ax | awk '{ print $1 }' | grep -e "^${mPID}$"`
			if [ "$isStart" != '' ];then
				echo "$NAME (pid `pidof $NAME`) already running."
				exit 1
			else
				echo "$NAME is stopped"
				exit 0
			fi
		else
			echo "$NAME is stopped"
			exit 0
        fi
        ;;
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;

    reload)
        echo -n "Reload service $NAME... "
		if [ -f $PIDFILE ];then
			mPID=`cat $PIDFILE`
			isStart=`ps ax | awk '{ print $1 }' | grep -e "^${mPID}$"`
			if [ "$isStart" != '' ];then
				$NGINX_BIN -s reload
				echo " done"
			else
				echo "$NAME is not running, can't reload."
				exit 1
			fi
		else
			echo "$NAME is not running, can't reload."
			exit 1
		fi
        ;;

    configtest)
        echo -n "Test $NAME configure files... "
        $NGINX_BIN -t
        ;;

    *)
        echo "Usage: $0 {start|stop|restart|reload|status|configtest}"
        exit 1
        ;;
esac
