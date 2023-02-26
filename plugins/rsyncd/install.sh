#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")
sysName=`uname`


#获取信息和版本
# bash /www/server/mdsever-web/scripts/getos.sh
bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`


if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

if id www &> /dev/null ;then 
    echo "www uid is `id -u www`"
    echo "www shell is `grep "^www:" /etc/passwd |cut -d':' -f7 `"
else
    groupadd www
	useradd -g www -s /bin/bash www
fi

echo $OSNAME
install_tmp=${rootPath}/tmp/mw_install.pl
Install_rsyncd()
{
	echo '正在安装脚本文件...' > $install_tmp
	

	if [ "$OSNAME" == "debian" ] || [ "$OSNAME" == "ubuntu" ];then
		apt install -y rsync
		apt install -y lsyncd
	elif [[ "$OSNAME" == "arch" ]]; then
		echo y | pacman -Sy rsync
		echo y | pacman -Sy lsyncd
	elif [[ "$OSNAME" == "macos" ]]; then
		# brew install rsync
		# brew install lsyncd
		echo "ok"
	else
		yum install -y rsync
		yum install -y lsyncd
	fi

	mkdir -p $serverPath/rsyncd
	mkdir -p $serverPath/rsyncd/receive
	mkdir -p $serverPath/rsyncd/send
	
	echo '2.0' > $serverPath/rsyncd/version.pl
	echo '安装完成' > $install_tmp
	cd ${rootPath} && python3 ${rootPath}/plugins/rsyncd/index.py start
	cd ${rootPath} && python3 ${rootPath}/plugins/rsyncd/index.py initd_install
}

Uninstall_rsyncd()
{
	if [ -f /usr/lib/systemd/system/rsyncd.service ] || [ -f /lib/systemd/system/rsyncd.service ];then
		systemctl stop rsyncd
		systemctl disable rsyncd
		rm -rf /usr/lib/systemd/system/rsyncd.service
		rm -rf /lib/systemd/system/rsyncd.service
		systemctl daemon-reload
	fi

	if [ -f /usr/lib/systemd/system/lsyncd.service ] || [ -f /lib/systemd/system/lsyncd.service ];then
		systemctl stop lsyncd
		systemctl disable lsyncd
		rm -rf /usr/lib/systemd/system/lsyncd.service
		rm -rf /lib/systemd/system/lsyncd.service
		systemctl daemon-reload
	fi

	if [ -f $serverPath/rsyncd/initd/rsyncd ];then
		$serverPath/rsyncd/initd/rsyncd stop
	fi
	
	rm -rf $serverPath/rsyncd
	echo "卸载完成" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_rsyncd
else
	Uninstall_rsyncd
fi
