#!/bin/bash

# 计划任务,恢复后,可自动拉起keepalived
# bash {$SERVER_PATH}/keepalived/scripts/chk_mysql.sh

counter=$(netstat -na|grep "LISTEN"|grep "3306"|wc -l)
data_time=`date +'%Y-%m-%d %H:%M:%S'`

if [ "${counter}" -eq "0" ]; then
    echo "${data_time}: start check mysql status, mysql is down, stop keepalive ..."
    systemctl stop keepalived
    echo "${data_time}: start check mysql end !!!"
fi


# 恢复后，自动拉起
# systemctl start keepalived
if [ "${counter}" -gt "0" ]; then
    echo "${data_time}: start check mysql status, mysql is up, start keepalive"

    keepalived_status=`which systemctl && systemctl status keepalived | grep Active | grep inactive`
    if [ "$keepalived_status" != "" ];then
        systemctl start keepalived
    fi
    
    echo "${data_time}: start check mysql end !!!"
fi
