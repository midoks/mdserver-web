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

UNINSTALL_MySQL()
{
    MYSQLD_CHECK=$(ps -ef |grep mysqld|grep -v grep|grep /www/server/mysql)
    if [ "$MYSQLD_CHECK" != "" ];then
        echo -e "----------------------------------------------------"
        echo -e "检查已有MySQL环境，卸载可能影响现有站点及数据"
        echo -e "----------------------------------------------------"
        echo -e "已知风险/输入yes强制卸载!"
        read -p "输入yes强制卸载: " yes;
        if [ "$yes" != "yes" ];then
            echo -e "------------"
            echo "取消卸载MySQL"
        else
            cd /www/server/mdserver-web/plugins/mysql && sh install.sh uninstall 8.0
        fi
    fi
}

UNINSTALL_MW()
{
    read -p "输入yes强制卸载面板: " yes;

    if [ "$yes" != "yes" ];then
        echo -e "------------"
        echo "取消卸载面板"
    else
        rm -rf /usr/bin/mw
        rm -rf /etc/init.d/mw
        systemctl daemon-reload
        rm -rf /www/server/mdserver-web
    fi
}


UNINSTALL_MySQL
UNINSTALL_MW

endTime=`date +%s`
((outTime=(${endTime}-${startTime})/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"
