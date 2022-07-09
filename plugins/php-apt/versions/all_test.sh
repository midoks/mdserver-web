#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")


## 

cd /www/server/mdserver-web

cd /www/server/mdserver-web/plugins/php-apt/versions && /bin/bash common.sh  5.6  install yaf