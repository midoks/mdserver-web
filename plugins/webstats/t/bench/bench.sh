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
# $RUN_CMD simple.lua

# $RUN_CMD  test_today.lua
# $RUN_CMD  test_time.lua

# $RUN_CMD  test_ngx_find.lua

$RUN_CMD  test_match_spider.lua