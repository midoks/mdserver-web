#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

cd /www/server/mdserver-web
if [ -f bin/activate ];then
	source bin/activate
fi