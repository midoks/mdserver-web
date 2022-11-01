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
echo "use system: ${_os}"

if [ "$EUID" -ne 0 ]
  then echo "Please run as root!"
  exit
fi

UNINSTALL_CHECK()
{
    echo -e "----------------------------------------------------"
    echo -e "暂时只能卸载OpenResty/PHP/MySQL/Redis/Memcached"
    echo -e "其他插件先手动卸载!"
    echo -e "----------------------------------------------------"
    echo -e "已知风险/输入yes强制卸载![yes/no]"
    read -p "输入yes强制卸载: " yes;
    if [ "$yes" != "yes" ];then
        echo -e "------------"
        echo "取消卸载"
        exit 1
    else
        echo "开始卸载!"
    fi
}


UNINSTALL_MySQL()
{
    MYSQLD_CHECK=$(ps -ef |grep mysqld | grep -v grep | grep /www/server/mysql)
    if [ "$MYSQLD_CHECK" != "" ];then
        echo -e "----------------------------------------------------"
        echo -e "检查已有MySQL环境，卸载可能影响现有站点及数据"
        echo -e "----------------------------------------------------"
        echo -e "已知风险/输入yes强制卸载![yes/no]"
        read -p "输入yes强制卸载: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "取消卸载MySQL"
        else
            cd /www/server/mdserver-web/plugins/mysql && sh install.sh uninstall 8.0
            echo "卸载MySQL成功!"
        fi
    fi
}

UNINSTALL_OP()
{
    if [ -f /www/server/openresty ];then
        echo -e "----------------------------------------------------"
        echo -e "检查已有OpenResty环境，卸载可能影响现有站点及数据"
        echo -e "----------------------------------------------------"
        echo -e "已知风险/输入yes强制卸载![yes/no]"
        read -p "输入yes强制卸载: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "取消卸载OpenResty"
        else
            cd /www/server/mdserver-web/plugins/openresty && sh install.sh uninstall
            echo "卸载OpenResty成功!"
        fi
    fi
}

UNINSTALL_PHP()
{
    if [ -d /www/server/php ];then
        echo -e "----------------------------------------------------"
        echo -e "检查已有PHP环境，卸载可能影响现有站点及数据"
        echo -e "----------------------------------------------------"
        read -p "输入yes强制卸载所有PHP[yes/no]: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "取消卸载PHP"
        else
            PHP_VER_LIST=(53 54 55 56 70 71 72 73 74 80 81 82)
            for PHP_VER in ${PHP_VER_LIST[@]}; do
                if [ -d /www/server/php/${PHP_VER} ];then
                    cd /www/server/mdserver-web/plugins/php && bash install.sh uninstall ${PHP_VER}
                fi
                echo "卸载PHP${PHP_VER}成功!"
            done
        fi
    fi
}

UNINSTALL_MEMCACHED()
{
    if [ -d /www/server/memcached ];then
        echo -e "----------------------------------------------------"
        echo -e "检查已有Memcached环境，卸载可能影响现有站点及数据"
        echo -e "----------------------------------------------------"
        read -p "输入yes强制卸载所有Memcached[yes/no]: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "取消卸载Memcached"
        else
            cd /www/server/mdserver-web/plugins/memcached && bash install.sh uninstall
            echo "卸载Memcached成功"
        fi
    fi
}

UNINSTALL_REDIS()
{
    if [ -d /www/server/redis ];then
        echo -e "----------------------------------------------------"
        echo -e "检查已有Redis环境，卸载可能影响现有站点及数据"
        echo -e "----------------------------------------------------"
        read -p "输入yes强制卸载所有Redis[yes/no]: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "取消卸载Redis"
        else
            cd /www/server/mdserver-web/plugins/redis && bash install.sh uninstall 7.0.4
            echo "卸载Redis成功"
        fi
    fi
}

UNINSTALL_MW()
{
    echo -e "----------------------------------------------------"
    echo -e "检查已有mderver-web环境，卸载可能影响现有站点及数据"
    echo -e "----------------------------------------------------"
    read -p "输入yes强制卸载面板: " yes;
    if [ "$yes" != "yes" ];then
        echo -e "------------"
        echo "取消卸载面板"
    else
        rm -rf /usr/bin/mw
        rm -rf /etc/init.d/mw
        systemctl daemon-reload
        rm -rf /www/server/mdserver-web
        echo "卸载面板成功"
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
