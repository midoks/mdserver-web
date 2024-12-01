#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sourcePath=${serverPath}/source/php

actionType=$1
version=$2

sysName=`uname`
LIBNAME=phalcon
LIBV=0


# if [ `echo "$version > 7.4"|bc` -eq 1 ];then
# 	echo "I won't support it"
# 	exit 0
# fi

CMD='apt '
if [ "$actionType" == 'install' ];then
	CMD="$CMD install -y php${version}-"
elif [ "$actionType" == 'uninstall' ];then
	CMD="$CMD uninstall -y php${version}-"
fi

if [ "$version" == '5.6' ];then
	CMD="${CMD}phalcon3"
elif [[ "$version" == '7.0' ]]; then
	CMD="${CMD}phalcon3"
elif [[ "$version" == '7.1' ]]; then
	CMD="${CMD}phalcon3"
elif [[ "$version" == '7.2' ]]; then
	CMD="${CMD}phalcon4"
elif [[ "$version" == '7.3' ]]; then
	CMD="${CMD}phalcon3"
elif [[ "$version" == '7.4' ]]; then
	CMD="${CMD}phalcon4"
elif [[ "$version" == '8.0' ]]; then
	CMD="${CMD}phalcon5"
elif [[ "$version" == '8.1' ]]; then
	CMD="${CMD}phalcon5"
elif [[ "$version" == '8.2' ]]; then
	CMD="${CMD}phalcon5"
elif [[ "$version" == '8.3' ]]; then
	CMD="${CMD}phalcon5"
elif [[ "$version" == '8.4' ]]; then
	CMD="${CMD}phalcon5"
fi

$CMD
echo "$CMD"
