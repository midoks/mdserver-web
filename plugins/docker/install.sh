#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

# cd /www/server/mdserver-web/plugins/docker && /bin/bash install.sh uninstall 1.0
# cd /www/server/mdserver-web/plugins/docker && /bin/bash install.sh install 1.0

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

# {
#     "registry-mirrors": [
#         "http://hub-mirror.c.163.com",
#         "https://docker.mirrors.ustc.edu.cn",
#         "https://registry.docker-cn.com"
#     ]
# }

# sudo mkdir -p /etc/docker
# sudo tee /etc/docker/daemon.json <<-'EOF'
# {
#     "registry-mirrors": [
#         "http://hub-mirror.c.163.com",
#         "https://docker.mirrors.ustc.edu.cn",
#         "https://registry.docker-cn.com"
#     ]
# }
# EOF
# sudo systemctl daemon-reload
# sudo systemctl restart docker

Install_Docker()
{
	# which docker
	# if [ "$?" == "0" ];then
	# 	echo '安装已经完成docker' > $install_tmp
	# 	exit 0
	# fi

	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	if [ ! -d  $serverPath/docker ];then
		curl -fsSL https://get.docker.com | bash
		mkdir -p $serverPath/docker
	fi

	pip install docker
	pip install pytz
	
	if [ -d $serverPath/docker ];then
		echo "${VERSION}" > $serverPath/docker/version.pl
		echo '安装完成' > $install_tmp

		cd ${rootPath} && python3 ${rootPath}/plugins/docker/index.py start
		cd ${rootPath} && python3 ${rootPath}/plugins/docker/index.py initd_install
	fi
}

Uninstall_Docker()
{
	CMD=yum
	which apt
	if [ "$?" == "0" ];then
		CMD=apt
	fi

	if [ -f /usr/lib/systemd/system/docker.service ];then
		systemctl stop docker
		systemctl disable docker
		rm -rf /usr/lib/systemd/system/docker.service
		systemctl daemon-reload
	fi

	$CMD remove -y docker docker-ce-cli containerd.io
	# docker-client \
	# docker-client-latest \
	# docker-common \
	# docker-latest \
	# docker-latest-logrotate \
	# docker-logrotate \
	# docker-selinux \
	# docker-engine-selinux \
	# docker-engine \
	# docker-ce

	rm -rf $serverPath/docker
	echo "Uninstall_Docker" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_Docker
else
	Uninstall_Docker
fi
