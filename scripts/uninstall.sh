#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export LANG=en_US.UTF-8
is64bit=`getconf LONG_BIT`

if [ -f /etc/motd ];then
    echo "" > /etc/motd
fi

startTime=`date +%s`

_os=`uname`
echo "检测到系统: ${_os}"

if [ "$EUID" -ne 0 ]
  then echo "需要使用 root 权限运行卸载脚本，请用 sudo 或切换到 root 后重试～"
  exit
fi

UNINSTALL_CHECK()
{
    echo -e "----------------------------------------------------"
    echo -e "目前支持卸载 OpenResty/PHP/MySQL/Redis/Memcached"
    echo -e "其他插件请先手动卸载哦！"
    echo -e "----------------------------------------------------"
    echo -e "温馨提示：输入 yes 才会继续卸载！[yes/no]"
    read -p "输入 yes 开始卸载（可随时 Ctrl+C 退出）: " yes;
    if [ "$yes" != "yes" ];then
        echo -e "------------"
        echo "已取消卸载，安全第一～"
        exit 1
    else
        echo "开始卸载！我们走～"
    fi
}


UNINSTALL_MySQL()
{
    MYSQLD_CHECK=$(ps -ef |grep mysqld | grep -v grep | grep /www/server/mysql)
    if [ "$MYSQLD_CHECK" != "" ];then
        echo -e "----------------------------------------------------"
        echo -e "检测到 MySQL，卸载可能影响站点与数据"
        echo -e "----------------------------------------------------"
        echo -e "温馨提示：输入 yes 才会继续卸载！[yes/no]"
        read -p "输入 yes 强制卸载: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "已取消卸载 MySQL"
        else
            cd /www/server/mdserver-web/plugins/mysql && sh install.sh uninstall 8.0
            echo "MySQL 卸载完成！"
        fi
    fi
}

UNINSTALL_OP()
{
    if [ -f /www/server/openresty ];then
        echo -e "----------------------------------------------------"
        echo -e "检测到 OpenResty，卸载可能影响站点与数据"
        echo -e "----------------------------------------------------"
        echo -e "温馨提示：输入 yes 才会继续卸载！[yes/no]"
        read -p "输入 yes 强制卸载: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "已取消卸载 OpenResty"
        else
            cd /www/server/mdserver-web/plugins/openresty && sh install.sh uninstall
            echo "OpenResty 卸载完成！"
        fi
    fi
}

UNINSTALL_PHP()
{
    if [ -d /www/server/php ];then
        echo -e "----------------------------------------------------"
        echo -e "检测到 PHP，卸载可能影响站点与数据"
        echo -e "----------------------------------------------------"
        read -p "输入 yes 强制卸载所有 PHP [yes/no]: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "已取消卸载 PHP"
        else
            PHP_VER_LIST=(53 54 55 56 70 71 72 73 74 80 81 82)
            for PHP_VER in ${PHP_VER_LIST[@]}; do
                if [ -d /www/server/php/${PHP_VER} ];then
                    cd /www/server/mdserver-web/plugins/php && bash install.sh uninstall ${PHP_VER}
                fi
                echo "PHP${PHP_VER} 卸载完成！"
            done
        fi
    fi
}

UNINSTALL_MEMCACHED()
{
    if [ -d /www/server/memcached ];then
        echo -e "----------------------------------------------------"
        echo -e "检测到 Memcached，卸载可能影响站点与数据"
        echo -e "----------------------------------------------------"
        read -p "输入 yes 强制卸载所有 Memcached [yes/no]: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "已取消卸载 Memcached"
        else
            cd /www/server/mdserver-web/plugins/memcached && bash install.sh uninstall
            echo "Memcached 卸载完成！"
        fi
    fi
}

UNINSTALL_REDIS()
{
    if [ -d /www/server/redis ];then
        echo -e "----------------------------------------------------"
        echo -e "检测到 Redis，卸载可能影响站点与数据"
        echo -e "----------------------------------------------------"
        read -p "输入 yes 强制卸载所有 Redis [yes/no]: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "已取消卸载 Redis"
        else
            cd /www/server/mdserver-web/plugins/redis && bash install.sh uninstall 7.0.4
            echo "Redis 卸载完成！"
        fi
    fi
}

UNINSTALL_MW()
{
    echo -e "----------------------------------------------------"
    echo -e "检测到面板环境，卸载可能影响站点与数据"
    echo -e "----------------------------------------------------"
    read -p "输入 yes 强制卸载面板（仅移除面板，不清理网站/数据库数据）: " yes;
    if [ "$yes" != "yes" ];then
        echo -e "------------"
        echo "已取消卸载面板"
    else
        rm -rf /usr/bin/mw
        rm -rf /etc/init.d/mw
        systemctl daemon-reload
        rm -rf /www/server/mdserver-web
        echo "面板卸载完成！"
    fi
}

UNINSTALL_CHECK

UNINSTALL_OP
UNINSTALL_PHP
UNINSTALL_MySQL
UNINSTALL_MEMCACHED
UNINSTALL_REDIS
UNINSTALL_MW

endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"
