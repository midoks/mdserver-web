#! /bin/sh
export PATH=$PATH:/opt/local/bin:/opt/local/sbin:/opt/local/share/man:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin:/opt/homebrew/bin
DIR=$(cd "$(dirname "$0")"; pwd)
ROOT_DIR=$(cd "$(dirname "$0")"; pwd)

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira && bash install.sh install 72
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions/common && bash mcrypt.sh install 82
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/lib && bash libmcrypt.sh

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/scripts/quick && bash debug.sh
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions && /bin/bash all_mac.sh

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira && bash install.sh install 55
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions/common && bash gd.sh install 73
# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/rapira/versions/common && bash swoole.sh install 54


# PHP_VER=52
# echo "php${PHP_VER} -- start"
# cmd_ext=$(ls -l $DIR/versions/$PHP_VER/ |awk '{print $9}')
# cd $DIR && /bin/bash install.sh install $PHP_VER
# for ii in $cmd_ext
# do
# 	if [ "install.sh" = "$ii" ];then
# 		echo '' > /tmp/t.log
# 	else
# 		cd $DIR/versions/$PHP_VER &&  /bin/bash $ii install $PHP_VER
# 	fi 
# done
# echo "php${PHP_VER} -- end"


PHP_VER_LIST=(84 85)
PHP_VER_LIST=(84)
for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"
	if [ ! -d  /Users/midoks/Desktop/mwdev/server/rapira/${PHP_VER} ];then
		cd /Users/midoks/Desktop/mwdev//server/mdserver-web/plugins/rapira && bash install.sh install ${PHP_VER}
	fi
	echo "php${PHP_VER} -- end"
done

cd $DIR
PHP_VER_LIST=(84)
# yar
PHP_EXT_LIST=(ZendGuardLoader pdo mysqlnd sqlite3 openssl opcache mcrypt fileinfo \
	exif gd intl pcntl memcache memcached redis imagemagick xdebug yac apc mongo mongodb mbstring iconv)

for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"

	if [ ! -d /Users/midoks/Desktop/mwdev/server/rapira/${PHP_VER} ];then
		echo "php${PHP_VER} is not install!"
		continue
	fi

	NON_ZTS_FILENAME=`ls /Users/midoks/Desktop/mwdev/server/rapira/${PHP_VER}/link/lib/php/extensions | grep no-debug-non-zts`
	for EXT in ${PHP_EXT_LIST[@]}; do
		extFile=/Users/midoks/Desktop/mwdev/server/rapira/${PHP_VER}/link/lib/php/extensions/${NON_ZTS_FILENAME}/${EXT}.so
		echo "${PHP_VER} ${EXT} start"
		if [ ! -f $extFile ];then
			bash common.sh $PHP_VER  install ${EXT}
		fi
		echo "${PHP_VER} ${EXT} end"
	done
	
	echo "php${PHP_VER} -- end"
done

