#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web && . /Users/midoks/Desktop/mwdev/server/mdserver-web/bin/activate && python3 /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/index.py install_pre_inspection 84
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira && bash install.sh install 84
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions && /bin/bash  common.sh 84 install redis

# cd /www/server/mdserver-web/plugins/rapira && bash install.sh install 73
# cd /www/server/mdserver-web/plugins/rapira && bash install.sh install 84
# cd /www/server/mdserver-web/plugins/rapira && bash install.sh install source
# 
# https://www.php.net/releases

# journalctl -u rapira84 -f

if id www &> /dev/null ;then 
    echo "www uid is `id -u www`"
    echo "www shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	useradd -g www -s /sbin/nologin www
	# useradd -g www -s /bin/bash www
fi

action=$1
type=$2

if [ "${2}" = "" ];then
	echo '缺少安装脚本.'
	exit 0
fi 

if [ ! -d $curPath/versions/$2 ];then
	echo '缺少安装脚本..'
	exit 0
fi

if [ "${action}" = "uninstall" ];then
	
	if [ -f /usr/lib/systemd/system/rapira${type}.service ] || [ -f /lib/systemd/system/rapira${type}.service ] ;then
		systemctl stop rapira${type}
		systemctl disable rapira${type}
		rm -rf /usr/lib/systemd/system/rapira${type}.service
		rm -rf /lib/systemd/system/rapira${type}.service
		systemctl daemon-reload
	fi
fi

cd ${curPath} && sh -x $curPath/versions/$2/install.sh $1


if [ "${action}" = "install" ] && [ -d ${serverPath}/rapira/${type} ];then
	#初始化
	echo "cd ${rootPath} && . bin/activate && python3 plugins/rapira/index.py start ${type}"
	echo "cd ${rootPath} && . bin/activate && python3 plugins/rapira/index.py initd_install ${type}"
	cd ${rootPath} && . bin/activate && python3 plugins/rapira/index.py start ${type}
	cd ${rootPath} && . bin/activate && python3 plugins/rapira/index.py initd_install ${type}

	# 安装通用扩展
	echo "install PHP${type} extend start"

	# cd /www/server/mdserver-web/plugins/rapira/versions && bash common.sh 84 install brotli
	# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions && bash common.sh 84 install brotli
	# cd ${rootPath}/plugins/rapira/versions && bash common.sh 84 install brotli

	# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions/common && bash brotli.sh install 84
	# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions/common && bash brotli.sh install 84

	cd ${rootPath}/plugins/rapira/versions/common && bash curl.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash gd.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash readline.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash iconv.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash exif.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash intl.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash mcrypt.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash openssl.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash bcmath.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash redis.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash memcached.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash pcntl.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash zip.sh install ${type}
	cd ${rootPath}/plugins/rapira/versions/common && bash zlib.sh install ${type}

	echo "install PHP${type} extend end"
fi



