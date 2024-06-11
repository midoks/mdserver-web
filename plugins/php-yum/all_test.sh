#! /bin/sh
export PATH=$PATH:/opt/local/bin:/opt/local/sbin:/opt/local/share/man:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin
DIR=$(cd "$(dirname "$0")"; pwd)


PHP_VER=71
echo "php${PHP_VER} -- start"
cmd_ext=$(ls -l $DIR/versions/$PHP_VER/ |awk '{print $9}')
cd $DIR && /bin/bash install.sh install $PHP_VER
for ii in $cmd_ext
do
	if [ "install.sh" == "$ii" ];then
		echo '' > /tmp/t.log
	else
		cd $DIR/versions/$PHP_VER &&  /bin/bash $ii install $PHP_VER
	fi 
done
echo "php${PHP_VER} -- end"


PHP_VER_LIST=(53 54 55 56 70 71 72 73 74 80 81 82 83)
# PHP_VER_LIST=(81)
for PHP_VER in ${PHP_VER_LIST[@]}; do
	echo "php${PHP_VER} -- start"
	if [ -d  /www/server/php/${PHP_VER} ];then
		cmd_ext=$(ls -l $DIR/versions/$PHP_VER/ |awk '{print $9}')
		for ii in $cmd_ext
		do
			echo "${ii}"
			if [ "install.sh" == "$ii" ];then
				echo '' > /tmp/t.log
			else
				cd $DIR/versions/$PHP_VER/ && bash $ii install ${PHP_VER}
			fi 
		done
	fi
	echo "php${PHP_VER} -- end"
done


rm -rf /tmp/t.log
