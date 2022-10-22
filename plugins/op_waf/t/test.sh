#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# apt -y install apache2-utils
# yum -y install httpd-tools

# ab -c 3000 -n 10000000 http://www.zzzvps.com/
# /cc https://www.zzzvps.com/ 120
# ab -c 10 -n 1000 http://t1.cn/wp-admin/index.php
# ab -c 1000 -n 1000000 http://dev156.cachecha.com/

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

python3 index.py
