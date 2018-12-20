#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin



mw_start(){
	gunicorn -c setting.py app:app &
	python task.py &
}


mw_start_debug(){
	python task.py &
	# gunicorn -b :7200 app:app
	gunicorn -c setting.py app:app
}

mw_stop()
{
	ps -ef|grep app:app |grep -v grep|awk '{print $2}'|xargs kill -9
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
esac