#!/bin/bash

date +'%Y-%m-%d %H:%M:%S'
echo "start check mysql status ..."
counter=$(netstat -na|grep "LISTEN"|grep "3306"|wc -l)
if [ "${counter}" -eq 0 ]; then
    echo "check mysql is down, stop keepalive"
    systemctl stop keepalived
fi

echo "start check mysql end"
date +'%Y-%m-%d %H:%M:%S'