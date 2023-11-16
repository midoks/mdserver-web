#!/bin/bash

# 计划任务,恢复后,可自动拉起keepalived
# bash {$SERVER_PATH}/keepalived/scripts/chk_mysql.sh

counter=$(netstat -na|grep "LISTEN"|grep "3306"|wc -l)

if [ "${counter}" -eq 0 ]; then
    echo "start check mysql status ..."
    date +'%Y-%m-%d %H:%M:%S'
    echo "check mysql is down, stop keepalive"
    systemctl stop keepalived
    date +'%Y-%m-%d %H:%M:%S'
    echo "start check mysql end !!!"
fi


# 恢复后，自动拉起
# systemctl start keepalived
if [ "${counter}" -gt 0 ]; then
    echo "start check mysql status ..."
    date +'%Y-%m-%d %H:%M:%S'
    echo "check mysql is up, start keepalive"

    keepalived_status=`systemctl status keepalived | grep Active | grep inactive`
    if [ "$keepalived_status" != "" ];then
        systemctl start keepalived
    fi
    date +'%Y-%m-%d %H:%M:%S'
    echo "start check mysql end !!!"
fi
