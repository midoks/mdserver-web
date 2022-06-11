#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8


wget -O /tmp/master.zip https://codeload.github.com/midoks/mdserver-web/zip/master
rm -rf /tmp/mdserver-web-master
cd /tmp && unzip  /tmp/master.zip
cp -rf /tmp/mdserver-web-master/* /www/server/mdserver-web
rm -rf /tmp/master.zip
rm -rf /tmp/mdserver-web-master
