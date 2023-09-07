#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi


GOGS_DOWNLOAD='https://dl.gogs.io'

getOs(){
	os=`uname`
	if [ "Darwin" == "$os" ];then
		echo 'darwin'
	else
		echo 'linux'
	fi
	return 0
}

getBit(){
	echo `getconf  LONG_BIT`
}


Install_gogs()
{
	
	mkdir -p $serverPath/source/gogs

	echo '正在安装脚本文件...' > $install_tmp
	version=$1
	os=`getOs`

	# if id git &> /dev/null ;then 
	#     echo "git uid is `id -u git`"
	#     echo "git shell is `grep "^git:" /etc/passwd |cut -d':' -f7 `"
	# else
	#     groupadd git
	# 	useradd -g git git
	# fi

	git config --global push.default simple

	if [ "darwin" == "$os" ];then
		file=gogs_${version}_darwin_amd64.zip
	else
		file=gogs_${version}_linux_amd64.zip
	fi

	if [ ! -f $serverPath/source/gogs/$file ];then
		wget  --no-check-certificate -O $serverPath/source/gogs/$file ${GOGS_DOWNLOAD}/${version}/${file}
	fi

	cd $serverPath/source/gogs && unzip -o $file -d gogs_${version}
	mv $serverPath/source/gogs/gogs_${version}/gogs/ $serverPath/gogs


	if [ -d $serverPath/gogs ];then
		echo $version > $serverPath/gogs/version.pl

		cd ${rootPath} && python3 ${rootPath}/plugins/gogs/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/gogs/index.py initd_install
	fi
	# if id -u gogs > /dev/null 2>&1; then
 #        echo "gogs user exists"
	# else
	# 	useradd gogs
	# 	cp /etc/sudoers{,.`date +"%Y-%m-%d_%H-%M-%S"`}
	# 	echo "gogs ALL=(ALL)    NOPASSWD: ALL" >> /etc/sudoers
	# fi

	echo 'install success' > $install_tmp
}

Uninstall_gogs()
{

	if [ -f /usr/lib/systemd/system/gogs.service ];then
		systemctl stop gogs
		systemctl disable gogs
		rm -rf /usr/lib/systemd/system/gogs.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/gogs/initd/gogs ];then
		$serverPath/gogs/initd/gogs stop
	fi

	rm -rf $serverPath/gogs
	echo 'uninstall success' > $install_tmp
}


action=$1
version=$2
if [ "${1}" == 'install' ];then
	Install_gogs $version
else
	Uninstall_gogs $version
fi
