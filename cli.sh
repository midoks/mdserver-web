#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
DIR=$(cd "$(dirname "$0")"; pwd)
MDIR=$(dirname "$DIR")

PATH=$PATH:$DIR/bin
if [ -f bin/activate ];then
	source bin/activate
fi

# export LC_ALL="en_US.UTF-8"

mw_start(){
	gunicorn -c setting.py app:app
	python3 task.py &
}


mw_start_debug(){
	
	python3 task.py &
	gunicorn -b :7200 -k gevent -w 1 app:app
	# gunicorn -b :7200 -k eventlet -w 1 app:app 
}

mw_start_debug2(){
	gunicorn -c setting.py app:app
	python3 task.py &
	
}


mw_stop()
{
	PLIST=`ps -ef|grep app:app |grep -v grep|awk '{print $2}'`
	for i in $PLIST
	do
	    kill -9 $i
	done
	ps -ef|grep task.py |grep -v grep|awk '{print $2}'|xargs kill -9
}

case "$1" in
    'start') mw_start;;
    'stop') mw_stop;;
    'restart') 
		mw_stop 
		mw_start
		;;
	'debug') 
		mw_stop 
		mw_start_debug
		;;
	'debug2') 
		mw_stop 
		mw_start_debug2
		;;
esac