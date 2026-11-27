#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/postgresql && bash install.sh install 18
# cd /www/server/mdserver-web/plugins/postgresql && bash install.sh install 19
# cd /www/server/mdserver-web && . bin/activate && python3 plugins/postgresql/index.py do_full_sync
# cd /www/server/mdserver-web && . bin/activate && python3 plugins/postgresql/index.py reload
# cd /www/server/mdserver-web && . bin/activate && python3 plugins/postgresql/index.py get_master_status {}
# cd /www/server/mdserver-web && . bin/activate && python3 plugins/postgresql/index.py run_info {}
# cd /www/server/mdserver-web && . bin/activate && python3 plugins/postgresql/index.py get_master_link {"page":1,"page_size":10}

# cd /www/server/mdserver-web && . bin/activate && python3 plugins/postgresql/index.py get_master_rep_slave_user_cmd {"username":"","db":""}
# ssh -vvv -i /tmp/pg_sync_id_rsa.txt -p 2022 -o IdentitiesOnly=yes root@1.1.1.1 "echo ok"
# ssh root@1.1.1.1 -i /tmp/pg_sync_id_rsa.txt -p 2022

# -- 主库
# CREATE TABLE t_test(id int primary key, ts timestamptz default now());
# INSERT INTO t_test VALUES (1);

# -- 备库（只读查询应能看到）
# SELECT * FROM t_test;

# 常用操作--终端
# -- 切换数据库
# \c ff

# -- 查看槽列表
# SELECT slot_name, active, pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)/1024/1024 AS retained_mb FROM pg_replication_slots;

# -- 查看主从状态列表 [主]
# SELECT * FROM pg_stat_replication;

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

if [ -f ${rootPath}/bin/activate ];then
	. ${rootPath}/bin/activate
fi

action=$1
type=$2

VERSION=(${type//./ })

if [ "${2}" = "" ];then
	echo '缺少安装脚本...'
	exit 0
fi 

if [ ! -d $curPath/versions/$VERSION ];then
	echo '缺少安装脚本2...'
	exit 0
fi

if id postgres &> /dev/null ;then 
    echo "postgres uid is `id -u postgres`"
    echo "postgres shell is `grep "^postgres:" /etc/passwd |cut -d':' -f7 `"
else
    which groupadd && groupadd postgres
	which useradd && useradd -g postgres postgres
fi

if [ "${action}" = "uninstall" ];then
	if [ -f /usr/lib/systemd/system/postgresql.service ] || [ -f /lib/systemd/system/postgresql.service ];then
		systemctl stop postgresql
		systemctl disable postgresql
		rm -rf /usr/lib/systemd/system/postgresql.service
		rm -rf /lib/systemd/system/postgresql.service
		systemctl daemon-reload
	fi
fi

sh -x $curPath/versions/$VERSION/install.sh $1

if [ "${action}" = "install" ] && [ -d $serverPath/postgresql ];then
	#初始化 
	cd ${rootPath} && python3 ${rootPath}/plugins/postgresql/index.py start ${type}
	cd ${rootPath} && python3 ${rootPath}/plugins/postgresql/index.py initd_install ${type}
fi
