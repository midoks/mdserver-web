#!/bin/bash

# 计划任务,恢复后,可自动拉起keepalived
# bash {$SERVER_PATH}/keepalived/scripts/chk.sh mysql

cd {$SERVER_PATH}/keepalived

# check script bash
curPath=`pwd`
rootPath=$(dirname "$curPath")

SOFT=$1

if [ "$SOFT" == "mysql" ];then
	bash ${rootPath}/keepalived/scripts/chk_mysql.sh > ${rootPath}/keepalived/keepalived.log
else
	echo "you should use [chk.sh mysql] exp ."
fi