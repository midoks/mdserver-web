#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8


mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/wwwlogs
mkdir -p /www/backup/database
mkdir -p /www/backup/site

echo "ubuntu dev ..."