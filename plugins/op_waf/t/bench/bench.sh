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
# $RUN_CMD test_gsub.lua

# $RUN_CMD --shdict 'limit 10m' test_find_server_name.lua
# $RUN_CMD --stap --shdict 'limit 10m' test_find_server_name.lua

# $RUN_CMD  test_rand.lua
# $RUN_CMD  test_ffi_time.lua
$RUN_CMD  test_get_cpu.lua