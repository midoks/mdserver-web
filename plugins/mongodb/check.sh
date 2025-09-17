#!/bin/bash

# MongoDB 监控脚本
# 功能：检查 MongoDB 是否运行，如果停止则自动重启

# MongoDB 服务名称（根据你的系统配置调整）
SERVICE_NAME="mongod"

# 检查 MongoDB 状态函数
check_mongodb() {
    # 检查 MongoDB 进程是否在运行
    if pgrep -x "$SERVICE_NAME" > /dev/null; then
        echo "$(date): MongoDB 正在运行"
        return 0
    else
        echo "$(date): MongoDB 已停止"
        return 1
    fi
}

# 重启 MongoDB 函数
restart_mongodb() {
    echo "$(date): 尝试重启 MongoDB..."
    
    # 根据你的系统选择适当的命令
    # 对于使用 systemd 的系统（如 Ubuntu 16.04+, CentOS 7+）
    if systemctl restart "mongodb"; then
        echo "$(date): MongoDB 重启成功"
        return 0
    else
        echo "$(date): MongoDB 重启失败"
        return 1
    fi
    
    # 对于使用 init.d 的系统
    # service mongod restart
}

if ! check_mongodb; then
    echo "$(date): 检测到 MongoDB 停止运行"
    restart_mongodb
fi
