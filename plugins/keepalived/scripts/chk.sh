#!/bin/bash



# check script bash
curPath=`pwd`
rootPath=$(dirname "$curPath")

SOFT=$1

if [ "$SOFT" == "mysql" ];then
	bash ${rootPath}/chk_mysql.sh
else
	echo "you should use [chk.sh mysql] exp ."
fi