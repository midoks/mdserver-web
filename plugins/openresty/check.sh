#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# OpenResty服务名称
service_name="openresty"

# 检查OpenResty是否正在运行
if systemctl is-active --quiet "$service_name"; then
    # 检查是否存在僵尸进程
    zombie_processes=$(ps -ef | grep -i openresty | grep -v grep | awk '{print $2}' | xargs ps -o state= -p 2>/dev/null | grep -c Z)
    if [ "$zombie_processes" -gt 0 ]; then
        echo "kill nginx 僵尸进程"
        ps -ef|grep nginx| grep -v grep| awk '{print $2}' | xargs kill -9
        echo "检测到OpenResty僵尸进程，正在重启服务..."
        systemctl restart "$service_name"
        echo "服务已重启"
    else
        echo "OpenResty运行正常"
    fi
else
    echo "kill nginx"
    ps -ef|grep nginx| grep -v grep| awk '{print $2}' | xargs kill -9
    echo "OpenResty未运行，正在启动服务..."
    systemctl start "$service_name"
    echo "服务已启动"
fi

NGINX_IDS=`ps -ef|grep nginx | grep -v grep| awk '{print $2}'`
if [ "$NGINX_IDS" == "" ];then
    ps -ef|grep nginx| grep -v grep| awk '{print $2}' | xargs kill -9
    systemctl start "$service_name"
    echo "OpenResty未运行，正在启动服务..."
fi

