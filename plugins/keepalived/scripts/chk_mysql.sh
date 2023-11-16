#!/bin/bash

# 计划任务,恢复后,可自动拉起keepalived
# {$SERVER_PATH}/keepalived/scripts/chk_mysql.sh

date +'%Y-%m-%d %H:%M:%S'
echo "start check mysql status ..."
counter=$(netstat -na|grep "LISTEN"|grep "3306"|wc -l)
if [ "${counter}" -eq 0 ]; then
    echo "check mysql is down, stop keepalive"
    systemctl stop keepalived
fi

echo "start check mysql end"
date +'%Y-%m-%d %H:%M:%S'