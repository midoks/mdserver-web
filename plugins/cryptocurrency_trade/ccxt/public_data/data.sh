#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
curPath=`pwd`

# bash plugins/cryptocurrency_trade/ccxt/public_data/data.sh

if [ -f ${curPath}/bin/activate ];then
	source ${curPath}/bin/activate
fi

python3 plugins/cryptocurrency_trade/ccxt/public_data/data.py long
