#!/bin/bash
# chkconfig: 2345 55 25
# description: MW Cloud Service

### BEGIN INIT INFO
# Provides:          Midoks
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts mw
# Description:       starts the mw
### END INIT INFO

RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
PLAIN='\033[0m'
BOLD='\033[1m'
SUCCESS='[\033[32mOK\033[0m]'
COMPLETE='[\033[32mDONE\033[0m]'
WARN='[\033[33mWARN\033[0m]'
ERROR='[\033[31mERROR\033[0m]'
WORKING='[\033[34m*\033[0m]'


PATH=/usr/local/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export LANG=en_US.UTF-8

PANEL_DIR={$SERVER_PATH}
ROOT_PATH=$(dirname "$PANEL_DIR")
PATH=$PATH:${PANEL_DIR}/bin


if [ -f ${PANEL_DIR}/bin/activate ];then
    source ${PANEL_DIR}/bin/activate
    if [ "$?" != "0" ];then
        echo "load local python env fail!"
    fi
fi

mw_start_panel()
{
    isStart=`ps -ef|grep 'gunicorn -c setting.py app:app' |grep -v grep|awk '{print $2}'`
    if [ "$isStart" == '' ];then
        echo -e "starting mw-panel... \c"
        cd ${PANEL_DIR}/web &&  gunicorn -c setting.py app:app
        port=$(cat ${PANEL_DIR}/data/port.pl)
        isStart=""
        while [[ "$isStart" == "" ]];
        do
            echo -e ".\c"
            sleep 0.5
            isStart=$(lsof -n -P -i:$port|grep LISTEN|grep -v grep|awk '{print $2}'|xargs)
            let n+=1
            if [ $n -gt 60 ];then
                break;
            fi
        done
        if [ "$isStart" == '' ];then
            echo -e "\033[31mfailed\033[0m"
            echo '------------------------------------------------------'
            tail -n 20 ${PANEL_DIR}/logs/panel_error.log
            echo '------------------------------------------------------'
            echo -e "\033[31mError: mw-panel service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo "starting mw-panel... mw(pid $(echo $isStart)) already running"
    fi
}


mw_start_task()
{
    isStart=$(ps aux |grep 'panel_task.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
        echo -e "starting mw-tasks... \c"
        cd ${PANEL_DIR} && python3 panel_task.py >> ${PANEL_DIR}/logs/panel_task.log 2>&1 &
        sleep 0.3
        isStart=$(ps aux |grep 'panel_task.py'|grep -v grep|awk '{print $2}')
        if [ "$isStart" == '' ];then
            echo -e "\033[31mfailed\033[0m"
            echo '------------------------------------------------------'
            tail -n 20 ${PANEL_DIR}/logs/panel_task.log
            echo '------------------------------------------------------'
            echo -e "\033[31mError: mw-tasks service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo "starting mw-tasks... mw-tasks (pid $(echo $isStart)) already running"
    fi
}

mw_start()
{
    mw_start_task
	mw_start_panel
}

# /www/server/mdserver-web/logs/panel_task.lock && service mw restart_task
mw_stop_task()
{
    if [ -f ${PANEL_DIR}/logs/panel_task.lock ];then
        echo -e "\033[32mthe task is running and cannot be stopped\033[0m"
        return 0
    fi

    echo -e "stopping mw-tasks... \c";
    panel_task=$(ps aux | grep 'panel_task.py'|grep -v grep|awk '{print $2}')
    panel_task=($panel_task)
    for p in ${panel_task[@]}
    do
        kill -9 $p  > /dev/null 2>&1
    done

    zzpids=$(ps -A -o stat,ppid,pid,cmd | grep -e '^[Zz]' | awk '{print $2}')
    zzpids=($zzpids)
    for p in ${zzpids[@]}
    do
        kill -9 $p > /dev/null 2>&1
    done
    echo -e "\033[32mdone\033[0m"
}

mw_stop_panel()
{
    echo -e "stopping mw-panel... \c";
    pidfile=${PANEL_DIR}/logs/mw.pid
    if [ -f $pidfile ];then
        pid=`cat $pidfile`
        kill -9 $pid > /dev/null 2>&1
        rm -f $pidfile
    fi

    APP_LIST=`ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}'`
    APP_LIST=($APP_LIST)
    for p in ${APP_LIST[@]}
    do
        kill -9 $p > /dev/null 2>&1
    done

    APP_LIST=`ps -ef|grep app:app |grep -v grep|awk '{print $2}'`
    APP_LIST=($APP_LIST)
    for i in ${APP_LIST[@]}
    do
        kill -9 $i > /dev/null 2>&1
    done
    echo -e "\033[32mdone\033[0m"
}

mw_stop()
{
    mw_stop_task
    mw_stop_panel
}

mw_status()
{
    isStart=$(ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}')
    if [ "$isStart" != '' ];then
        echo -e "\033[32mmw (pid $(echo $isStart)) already running\033[0m"
    else
        echo -e "\033[31mmw not running\033[0m"
    fi
    
    isStart=$(ps aux |grep 'panel_task.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" != '' ];then
        echo -e "\033[32mmw-task (pid $isStart) already running\033[0m"
    else
        echo -e "\033[31mmw-task not running\033[0m"
    fi
}


mw_reload()
{
	isStart=$(ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}')
    
    if [ "$isStart" != '' ];then
    	echo -e "reload mw... \c";
	    arr=`ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}'`
		for p in ${arr[@]}
        do
                kill -9 $p
        done
        cd ${PANEL_DIR}/web && gunicorn -c setting.py app:app
        isStart=`ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}'`
        if [ "$isStart" == '' ];then
            echo -e "\033[31mfailed\033[0m"
            echo '------------------------------------------------------'
            tail -n 20 $mw_path/logs/error.log
            echo '------------------------------------------------------'
            echo -e "\033[31mError: mw service startup failed.\033[0m"
            return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo -e "\033[31mmw not running\033[0m"
        mw_start
    fi
}

mw_close(){
    cd ${PANEL_DIR} && python3 panel_tools.py cli 14
}

mw_open()
{
    cd ${PANEL_DIR} && python3 panel_tools.py cli 15
}

mw_unbind_domain()
{
    if [ -f ${PANEL_DIR}/data/bind_domain.pl ];then
        rm -rf ${PANEL_DIR}/data/bind_domain.pl
    fi
}

mw_unbind_ssl()
{
    if [ -f ${PANEL_DIR}/local ];then
        rm -rf ${PANEL_DIR}/local
    fi

    if [ -f $mw_path/nginx ];then
        rm -rf $mw_path/nginx
    fi

    if [ -f $mw_path/ssl/choose.pl ];then
        rm -rf $mw_path/ssl/choose.pl
    fi
}

error_logs()
{
	tail -n 100 ${PANEL_DIR}/logs/panel_error.log
}

mw_install(){
   if [ -f ${PANEL_DIR}/task.py ];then
        echo "与后续版本差异太大,不再提供更新"
        exit 0
    fi

    LOCAL_ADDR=common
    cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
    if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
        LOCAL_ADDR=cn
    fi
    
    if [ "$LOCAL_ADDR" == "common" ];then
        curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/install.sh | bash
    else
        curl --insecure -fsSL  https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/install.sh | bash
    fi 
}

mw_update()
{
    if [ -f ${PANEL_DIR}/task.py ];then
        echo "与后续版本差异太大,不再提供更新"
        exit 0
    fi

    LOCAL_ADDR=common
    cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
    if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
        LOCAL_ADDR=cn
    fi
    
    if [ "$LOCAL_ADDR" == "common" ];then
        curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/update.sh | bash
    else
        curl --insecure -fsSL  https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/update.sh | bash
    fi
}

mw_update_dev()
{
    if [ -f ${PANEL_DIR}/task.py ];then
        echo "与后续版本差异太大,不再提供更新"
        exit 0
    fi
    
    LOCAL_ADDR=common
    cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
    if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
        LOCAL_ADDR=cn
    fi
    
    if [ "$LOCAL_ADDR" == "common" ];then
        curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update_dev.sh | bash
    else
        curl --insecure -fsSL https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/update_dev.sh | bash
    fi
    cd ${PANEL_DIR}
}

mw_update_venv()
{
    rm -rf ${PANEL_DIR}/bin
    rm -rf ${PANEL_DIR}/lib64
    rm -rf ${PANEL_DIR}/lib

    LOCAL_ADDR=common
    cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
    if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
        LOCAL_ADDR=cn
    fi
    
    if [ "$LOCAL_ADDR" == "common" ];then
        curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update_dev.sh | bash
    else
        curl --insecure -fsSL https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/update_dev.sh | bash
    fi
    cd ${PANEL_DIR}
}

mw_mirror()
{
    LOCAL_ADDR=common
    cn=$(curl -fsSL -m 10 -s http://ipinfo.io/json | grep "\"country\": \"CN\"")
    if [ ! -z "$cn" ] || [ "$?" == "0" ] ;then
        LOCAL_ADDR=cn
    fi

    if [ "$LOCAL_ADDR" == "common" ];then
        bash <(curl --insecure -sSL https://raw.githubusercontent.com/midoks/change-linux-mirrors/main/change-mirrors.sh)
    else
        bash <(curl --insecure -sSL https://gitee.com/SuperManito/LinuxMirrors/raw/main/ChangeMirrors.sh)
    fi
    cd ${ROOT_PATH}
}

mw_install_app()
{
    bash $mw_path/scripts/quick/app.sh
}

mw_close_admin_path(){
    cd ${PANEL_DIR} && python3 panel_tools.py cli 6
}

mw_force_kill()
{
    PLIST=`ps -ef|grep app:app |grep -v grep|awk '{print $2}'`
    for i in $PLIST
    do
        kill -9 $i
    done

    pids=`ps -ef|grep task.py | grep -v grep |awk '{print $2}'`
    arr=($pids)
    for p in ${arr[@]}
    do
        kill -9 $p
    done
}

mw_debug(){
    mw_stop
    mw_force_kill

    port=7200    
    if [ -f ${PANEL_DIR}/data/port.pl ];then
        port=$(cat ${PANEL_DIR}/data/port.pl)
    fi

    if [ -d ${PANEL_DIR}/web ];then
        cd ${PANEL_DIR}/web
    fi
    # gunicorn -b :$port -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1  app:app
    gunicorn -b :$port -k eventlet -w 1  app:app
}


function AutoSizeStr(){
    NAME_STR=$1
    NAME_NUM=$2

    NAME_STR_LEN=`echo "$NAME_STR" | wc -L`
    NAME_NUM_LEN=`echo "$NAME_NUM" | wc -L`

    fix_len=35
    remaining_len=`expr $fix_len - $NAME_STR_LEN - $NAME_NUM_LEN`
    FIX_SPACE=' '
    for ((ass_i=1;ass_i<=$remaining_len;ass_i++))
    do 
        FIX_SPACE="$FIX_SPACE "
    done
    echo -e " ❖   ${1}${FIX_SPACE}${2})"
}

mw_connect_mysql(){
    # choose mysql login

    declare -A DB_TYPE

    if [ -d "${ROOT_PATH}/mysql" ];then
        DB_TYPE["mysql"]="mysql"
    fi

    if [ -d "${ROOT_PATH}/mariadb" ];then
        DB_TYPE["mariadb"]="mariadb"
    fi

    if [ -d "${ROOT_PATH}/mysql-apt" ];then
        DB_TYPE["mysql-apt"]="mysql-apt"
    fi

    if [ -d "${ROOT_PATH}/mysql-yum" ];then
        DB_TYPE["mysql-yum"]="mysql-yum"
    fi

    if [ -d "${ROOT_PATH}/mysql-community" ];then
        DB_TYPE["mysql-community"]="mysql-community"
    fi

    SOURCE_LIST_KEY_SORT_TMP=$(echo ${!DB_TYPE[@]} | tr ' ' '\n' | sort -n)
    SOURCE_LIST_KEY=(${SOURCE_LIST_KEY_SORT_TMP//'\n'/})
    SOURCE_LIST_LEN=${#DB_TYPE[*]}

    if [ "$SOURCE_LIST_LEN" == "0" ]; then
        echo -e "no data!"
        exit 1
    fi

    cm_i=0
    for M in ${SOURCE_LIST_KEY[@]}; do
        num=`expr $cm_i + 1`
        AutoSizeStr "${M}" "$num"
        cm_i=`expr $cm_i + 1`
    done
    CHOICE_A=$(echo -e "\n${BOLD}└─ Please select and enter the database you want to log in to [ 1-${SOURCE_LIST_LEN} ]：${PLAIN}")
    read -p "${CHOICE_A}" INPUT

    if [ "$INPUT" == "" ]; then
        INPUT=1
    fi

    if [ "$INPUT" -lt "0" ] || [ "$INPUT" -gt "${SOURCE_LIST_LEN}" ]; then
        echo -e "\nBoundary error not selected!"
        exit 1
    fi

    INPUT=`expr $INPUT - 1`
    INPUT_KEY=${SOURCE_LIST_KEY[$INPUT]}
    CHOICE_DB=${DB_TYPE[$INPUT_KEY]}
    echo "login to ${CHOICE_DB}:"

    pwd=$(cd ${ROOT_PATH}/mdserver-web && python3 ${ROOT_PATH}/mdserver-web/plugins/${CHOICE_DB}/index.py root_pwd)
    if [ "$pwd" == "admin" ];then
        pwd=""
    fi

    if [ "$CHOICE_DB" == "mysql" ];then
        ${ROOT_PATH}/mysql/bin/mysql -uroot -p"${pwd}"
    fi

    if [ "$CHOICE_DB" == "mariadb" ];then
        ${ROOT_PATH}/mariadb/bin/mariadb  -S ${ROOT_PATH}/mariadb/mysql.sock -uroot -p"${pwd}"
    fi

    if [ "$CHOICE_DB" == "mysql-community" ];then
        ${ROOT_PATH}/mysql-community/bin/mysql -S ${ROOT_PATH}/mysql-community/mysql.sock -uroot -p"${pwd}"
    fi

    if [ "$CHOICE_DB" == "mysql-apt" ];then
        ${ROOT_PATH}/mysql-apt/bin/usr/bin/mysql -S ${ROOT_PATH}/mysql-apt/mysql.sock -uroot -p"${pwd}"
    fi

    if [ "$CHOICE_DB" == "mysql-yum" ];then
        ${ROOT_PATH}/mysql-yum/bin/usr/bin/mysql -S ${ROOT_PATH}/mysql-yum/mysql.sock -uroot -p"${pwd}"
    fi
}


mw_connect_pgdb(){
    if [ ! -d "${ROOT_PATH}/postgresql" ];then
        echo -e "postgresql not install!"
        exit 1
    fi


    pwd=$(cd ${PANEL_DIR} && python3 ${PANEL_DIR}/plugins/postgresql/index.py root_pwd)
    export PGPASSWORD=${pwd}
    echo "${ROOT_PATH}/postgresql/bin/psql -U postgres -W"
    ${ROOT_PATH}/postgresql/bin/psql -U postgres -W
}


mw_mongodb(){
    CONF="${ROOT_PATH}/mongodb/mongodb.conf"
    if [ ! -f "$CONF" ]; then
        echo -e "not install mongodb!"
        exit 1
    fi

    MGDB_PORT=$(cat $CONF |grep port|grep -v '#'|awk '{print $2}')
    MGDB_AUTH=$(cat $CONF |grep authorization | grep -v '#'|awk '{print $2}')

    AUTH_STR=""
    if [[ "$MGDB_AUTH" == "enabled" ]];then
        pwd=$(cd ${PANEL_DIR} && python3 ${PANEL_DIR}/plugins/mongodb/index.py root_pwd)
        AUTH_STR="-u root -p ${pwd}"
    fi

    CLIEXEC="${ROOT_PATH}/mongodb/bin/mongosh --port ${MGDB_PORT} ${AUTH_STR}"
    echo $CLIEXEC
    ${CLIEXEC}
}


mw_redis(){
    CONF="${ROOT_PATH}/redis/redis.conf"

    if [ ! -f "$CONF" ]; then
        echo -e "not install redis!"
        exit 1
    fi

    REDISPORT=$(cat $CONF |grep port|grep -v '#'|awk '{print $2}')
    REDISPASS=$(cat $CONF |grep requirepass|grep -v '#'|awk '{print $2}')
    if [ "$REDISPASS" != "" ];then
        REDISPASS=" -a $REDISPASS"
    fi
    CLIEXEC="${ROOT_PATH}/redis/bin/redis-cli -p $REDISPORT$REDISPASS"
    echo $CLIEXEC
    ${CLIEXEC}
}

mw_valkey(){
    CONF="${ROOT_PATH}/valkey/valkey.conf"

    if [ ! -f "$CONF" ]; then
        echo -e "not install valkey!"
        exit 1
    fi

    REDISPORT=$(cat $CONF |grep port|grep -v '#'|awk '{print $2}')
    REDISPASS=$(cat $CONF |grep requirepass|grep -v '#'|awk '{print $2}')
    if [ "$REDISPASS" != "" ];then
        REDISPASS=" -a $REDISPASS"
    fi
    CLIEXEC="${ROOT_PATH}/valkey/bin/valkey-cli -p $REDISPORT$REDISPASS"
    echo $CLIEXEC
    ${CLIEXEC}
}

mw_venv(){
    cd ${PANEL_DIR} && source bin/activate
}

mw_clean_lib(){
    cd ${PANEL_DIR} && rm -rf lib
    cd ${PANEL_DIR} && rm -rf lib64
    cd ${PANEL_DIR} && rm -rf bin
    cd ${PANEL_DIR} && rm -rf include
}

mw_list(){
    echo -e "mw default      - 显示面板默认信息"
    echo -e "mw db           - 连接MySQL"
    echo -e "mw pgdb         - 连接PostgreSQL"
    echo -e "mw mongdb       - 连接MongoDB"
    echo -e "mw redis        - 连接Redis"
    echo -e "mw valkey       - 连接WalKey"
    echo -e "mw install      - 执行安装脚本"
    echo -e "mw update       - 更新到正式环境最新代码"
    echo -e "mw update_dev   - 更新到测试环境最新代码"
    echo -e "mw debug        - 调式开发面板"
    echo -e "mw list         - 显示命令列表"
}

mw_default(){
    cd ${PANEL_DIR}
    port=7200
    scheme=$(cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py panel_ssl_type)
    
    if [ -f ${PANEL_DIR}/data/port.pl ];then
        port=$(cat ${PANEL_DIR}/data/port.pl)
    fi

    if [ ! -f ${PANEL_DIR}/data/default.pl ];then
        echo -e "\033[33mInstall Failed\033[0m"
        exit 1
    fi

    password=$(cat ${PANEL_DIR}/data/default.pl)

    admin_path=$(cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py admin_path)
    if [ "$address" == "" ];then
        v4=$(cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py getServerIp 4)
        v6=$(cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py getServerIp 6)

        if [ "$v4" != "" ] && [ "$v6" != "" ]; then

            if [ ! -f ${PANEL_DIR}/data/ipv6.pl ];then
                echo 'True' > ${PANEL_DIR}/data/ipv6.pl
                mw_stop
                mw_start
            fi

            address="MW-PANEL-URL-IPV4: ${scheme}://$v4:$port$admin_path \nMW-PANEL-URL-IPV6: ${scheme}://[$v6]:$port$admin_path"
        elif [ "$v4" != "" ]; then
            address="MW-PANEL-URL: ${scheme}://$v4:$port$admin_path"
        elif [ "$v6" != "" ]; then

            if [ ! -f ${PANEL_DIR}/data/ipv6.pl ];then
                #  Need to restart ipv6 to take effect
                echo 'True' > ${PANEL_DIR}/data/ipv6.pl
                mw_stop
                mw_start
            fi
            address="MW-PANEL-URL: ${scheme}://[$v6]:$port$admin_path"
        else
            address="MW-PANEL-URL: ${scheme}://you-network-ip:$port$admin_path"
        fi
    else
        address="MW-PANEL-URL: ${scheme}://$address:$port$admin_path"
    fi

    # bind domain check
    panel_bind_domain=$(cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py panel_bind_domain)
    if [ "$panel_bind_domain" != "" ];then
        address="MW-PANEL-URL: ${scheme}://$panel_bind_domain:$port$admin_path\n${address}"
    fi

    show_panel_ip="$port|"
    echo -e "=================================================================="
    echo -e "\033[32mMW-PANEL DEFAULT INFO!\033[0m"
    echo -e "=================================================================="
    echo -e "$address"
    echo -e `cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py username`
    echo -e `cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py password`
    echo -e "\033[33mWarning:\033[0m"
    echo -e "\033[33mIf you cannot access the panel. \033[0m"
    echo -e "\033[33mrelease the following port (${show_panel_ip}80|443|22) in the security group.\033[0m"
    echo -e "=================================================================="
}

case "$1" in
    'start') mw_start;;
    'stop') mw_stop;;
    'reload') mw_reload;;
    'restart') 
        mw_stop
        mw_start;;
    'restart_panel')
        mw_stop_panel
        mw_start_panel;;
    'restart_task')
        mw_stop_task
        mw_start_task;;
    'status') mw_status;;
    'logs') error_logs;;
    'close') mw_close;;
    'open') mw_open;;
    'install') mw_install;;
    'update') mw_update;;
    'dev') mw_update_dev;;
    'update_dev') mw_update_dev;;
    'install_app') mw_install_app;;
    'close_admin_path') mw_close_admin_path;;
    'unbind_domain') mw_unbind_domain;;
    'unbind_ssl') mw_unbind_domain;;
    'debug') mw_debug;;
    'mirror') mw_mirror;;
    'db') mw_connect_mysql;;
    'pgdb') mw_connect_pgdb;;
    'redis') mw_redis;;
    'valkey')mw_valkey;;
    'mongodb') mw_mongodb;;
    'venv') mw_update_venv;;
    'clean_lib') mw_clean_lib;;
    'list') mw_list;;
    'default') mw_default;;
    *)
        cd ${PANEL_DIR} && python3 ${PANEL_DIR}/panel_tools.py cli $1
        ;;
esac
