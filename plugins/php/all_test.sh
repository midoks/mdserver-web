#! /bin/sh
export PATH=$PATH:/opt/local/bin:/opt/local/sbin:/opt/local/share/man:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin
DIR=$(cd "$(dirname "$0")"; pwd)


PHP_VER=53
echo "php${PHP_VER} -- start"
cmd_ext=$(ls -l $DIR/versions/$PHP_VER/ |awk '{print $9}')
cd $DIR/versions/$PHP_VER && sh install.sh
for ii in $cmd_ext
do
	if [ "install.sh" == "$ii" ];then
		echo ''
	else
		cd $DIR/versions/$PHP_VER &&  /bin/bash $ii install $PHP_VER
	fi 
done
echo "php${PHP_VER} -- end"


