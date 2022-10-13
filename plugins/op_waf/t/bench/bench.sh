#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

# echo $rootPath

resty=$rootPath/openresty/bin/resty

RUN_CMD=$resty
if [ ! -f $resty ];then
	RUN_CMD=/www/server/openresty/bin/resty
fi


# test
# $RUN_CMD a.lua

$RUN_CMD test_gsub.lua

