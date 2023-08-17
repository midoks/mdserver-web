#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4
# cd /www/server/mdserver-web/plugins/mongodb && /bin/bash install.sh install 5.0.4

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

sysName=`uname`
echo "use system: ${sysName}"

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
SYS_VERSION_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


Install_app_mac()
{
	mkdir -p $serverPath/mongodb
	if [ "$VERSION" == "5.0" ];then
		G_VERSION="5.0.11"
	elif [[ "$VERSION" == "4.4" ]]; then
		G_VERSION="4.4.11"
	fi

	if [ ! -f $serverPath/source/mongodb-macos-x86_64-${G_VERSION}.tgz ];then
		wget -O $serverPath/source/mongodb-macos-x86_64-${G_VERSION}.tgz https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-${G_VERSION}.tgz
	fi

	cd $serverPath/source && tar -zxvf mongodb-macos-x86_64-${G_VERSION}.tgz
	cd  mongodb-macos-x86_64-${G_VERSION} && mv  ./* $serverPath/mongodb
}


Install_Linux_Ubuntu()
{
##################### Ubuntu start #####################
if [ "$SYS_VERSION_ID" == "22" ]; then
	echo "Not yet supported"
	exit 1
fi




echo $SYS_VERSION_ID

SOURCE_NAME=bionic
if [ "$SYS_VERSION_ID" == "18.04" ];then
	SOURCE_NAME=bionic
elif [ "$SYS_VERSION_ID" == "16.04" ];then
	SOURCE_NAME=xenial
elif [ "$SYS_VERSION_ID" == "20.04" ];then
	SOURCE_NAME=focal
fi

# wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
# apt install -y gnupg
# touch /etc/apt/sources.list.d/mongodb-org-4.4.list
# echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list


wget -qO - https://www.mongodb.org/static/pgp/server-${VERSION}.asc | sudo apt-key add -
apt install -y gnupg
touch /etc/apt/sources.list.d/mongodb-org-${VERSION}.list
lsb_release -dc

echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu ${SOURCE_NAME}/mongodb-org/${VERSION} multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-${VERSION}.list

apt update -y
apt install -y mongodb-org
##################### Ubuntu  end #####################
}


Uninstall_Linux_Ubuntu()
{
	
if [ -f /lib/systemd/system/mongod.service ] || [ -f /usr/lib/systemd/system/mongod.service ] ;then
	systemctl stop mongod
fi



apt purge -y mongodb-org*
apt autoremove -y
rm -r /var/log/mongodb
rm -r /var/lib/mongodb
}


Install_Linux_Debian()
{
##################### debian start #####################
if [ "$SYS_VERSION_ID" -eq "11" ] && [ "$VERSION" -eq "4.4" ]; then
	echo "Not yet supported"
	exit 1
fi


if [ -f /usr/lib/systemd/system/mongod.service ];then
	echo 'alreay install exist!'
	exit 0
fi

wget -qO - https://www.mongodb.org/static/pgp/server-${VERSION}.asc | sudo apt-key add -
apt install -y gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-${VERSION}.asc | sudo apt-key add -

echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/${VERSION} main" | sudo tee /etc/apt/sources.list.d/mongodb-org-${VERSION}.list

apt update -y
apt install -y mongodb-org


echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections

##################### debian end #####################
}



Uninstall_Linux_Debian()
{
systemctl stop mongod
apt purge -y mongodb-org*
apt autoremove -y
rm -r /var/log/mongodb
rm -r /var/lib/mongodb
}


Install_Linux_Opensuse()
{
##################### opensuse start #####################
if [ "$SYS_VERSION_ID" -gt "15" ]; then
	echo "Not yet supported"
	exit 1
fi


if [ -f /usr/lib/systemd/system/mongod.service ];then
	echo 'alreay exist!'
	exit 0
fi

rpm --import https://www.mongodb.org/static/pgp/server-${VERSION}.asc
zypper addrepo --gpgcheck "https://repo.mongodb.org/zypper/suse/15/mongodb-org/${VERSION}/x86_64/" mongodb
zypper -n install mongodb-org
# zypper install mongodb-org-4.4.15 mongodb-org-server-4.4.15 mongodb-org-shell-4.4.15 mongodb-org-mongos-4.4.15 mongodb-org-tools-4.4.15


##################### opensuse end #####################
}


Uninstall_Linux_Opensuse()
{
systemctl stop mongod
zypper remove -y $(rpm -qa | grep mongodb-org)
rm -r /var/log/mongodb
rm -r /var/lib/mongo
}




# https://repo.mongodb.org/yum/redhat/7/mongodb-org/5.0/x86_64/RPMS/mongodb-org-server-5.0.4-1.el7.x86_64.rpm
Install_Linux_CentOS()
{
if [ -f /usr/lib/systemd/system/mongod.service ];then
	echo 'alreay exist!'
	exit 0
fi
#清空mongo的repo源
rm -rf /etc/yum.repos.d/mongodb-org-*
##################### centos start #####################
echo "
[mongodb-org-${VERSION}]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/${VERSION}/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-${VERSION}.asc
" > /etc/yum.repos.d/mongodb-org-${VERSION}.repo

yum install -y mongodb-org
##################### centos end #####################
}

Uninstall_Linux_CentOS()
{
systemctl stop mongod
yum erase -y $(rpm -qa | grep mongodb-org)
rm -r /var/log/mongodb
rm -r /var/lib/mongo
rm -rf /etc/yum.repos.d/mongodb-org-${VERSION}.repo
}


Install_app_linux()
{
	if [ "$OSNAME" == "ubuntu" ];then
		Install_Linux_Ubuntu
	elif [ "$OSNAME" == "debian" ];then
		Install_Linux_Debian
	elif [ "$OSNAME" == "centos" ];then
		Install_Linux_CentOS
	elif [ "$OSNAME" == "opensuse" ];then
		Install_Linux_Opensuse
	else 
		echo "Not yet supported"
		exit 1
	fi
}


Install_app()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source
	
	if [ "macos" == "$OSNAME" ];then
		Install_app_mac
	else
		Install_app_linux
	fi

	if [ "$?" == "0" ];then
		mkdir -p $serverPath/mongodb
		echo "${VERSION}" > $serverPath/mongodb/version.pl
		echo '安装完成' > $install_tmp

		#初始化 
		cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/mongodb/index.py initd_install
	fi
}



Uninstall_app_linux()
{
##################
if [ "$OSNAME" == "ubuntu" ];then
	Uninstall_Linux_Ubuntu
elif [ "$OSNAME" == "debian" ];then
	Uninstall_Linux_Debian
elif [ "$OSNAME" == "centos" ];then
	Uninstall_Linux_CentOS
elif [ "$OSNAME" == "opensuse" ];then
	Uninstall_Linux_Opensuse
else 
	echo "ok"
fi
##################
}

Uninstall_app()
{
	if [ "macos" == "$OSNAME" ];then
		echo 'mac'
	else
		Uninstall_app_linux
	fi

	rm -rf $serverPath/mongodb
	echo "Uninstall_mongodb" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_app
else
	Uninstall_app
fi
