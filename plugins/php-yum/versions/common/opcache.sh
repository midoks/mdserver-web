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
LIBNAME=opcache

cfgDir=/etc/opt/remi

OP_BL=${serverPath}/server/php-yum/opcache-blacklist.txt
if [ ! -f $OP_BL ];then
	touch $OP_BL
fi
ext_dir=${cfgDir}/php${version}/php.d
ext_file=${ext_dir}/10-opcache.ini

echo $ext_file

if [ "$actionType" == 'install' ];then
	yum install -y php${version}-php-${LIBNAME}
	echo "ls ${cfgDir}/php${version}/php.d | grep "${LIBNAME}.ini"| cut -d \  -f 1"
	find_opcache=`ls ${cfgDir}/php${version}/php.d | grep "${LIBNAME}.ini"| cut -d \  -f 1`
	echo $find_opcache
	if [ "$find_opcache" != "" ];then
		ext_file=${ext_dir}/${find_opcache}
	fi
	echo $ext_file
	echo "zend_extension=${LIBNAME}" >> $ext_file
	echo "opcache.enable=1" >> $ext_file
	echo "opcache.memory_consumption=128" >> $ext_file
	echo "opcache.interned_strings_buffer=8" >> $ext_file
	echo "opcache.max_accelerated_files=4000" >> $ext_file
	echo "opcache.revalidate_freq=60" >> $ext_file
	echo "opcache.fast_shutdown=1" >> $ext_file
	echo "opcache.enable_cli=1" >> $ext_file
	echo "opcache.jit=1205" >> $ext_file
	echo "opcache.jit_buffer_size=64M" >> $ext_file
	echo "opcache.save_comments=0" >> $ext_file
	echo "opcache.blacklist_filename=${OP_BL}" >> $ext_file
elif [ "$actionType" == 'uninstall' ];then
	if [ -f ${ext_dir}/10-opcache.ini.rpmsave ];then
		ext_file=${ext_dir}/10-opcache.ini.rpmsave
	fi

	# yum remove -y php83-php-opcache
	yum remove -y php${version}-php-${LIBNAME}
	rm -rf $ext_file
	echo 'cannot uninstall'
fi