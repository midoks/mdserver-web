#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /www/server/mdserver-web/plugins/gdrive && /bin/bash install.sh install 2.0


curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

PATH=$PATH:${rootPath}/bin
export PATH

if [ -f ${rootPath}/bin/activate ];then
    source ${rootPath}/bin/activate
fi

VERSION=$2

Install_App()
{
    tmp_ping=`ping -c 1 google.com 2>&1`
    echo $tmp_ping
    if [ $? -eq 0 ];then
        tmp=`python -V 2>&1|awk '{print $2}'`
        pVersion=${tmp:0:3}


        which pip
        if [ "$?" -eq "0" ];then
            tmp=$(pip list|grep google-api-python-client|awk '{print $2}')
            if [ "$tmp" != '2.39.0' ];then
                pip install --upgrade google-api-python-client
                # pip uninstall google-api-python-client -y
                pip install -I google-api-python-client==2.39.0 -i https://pypi.Python.org/simple
            fi
            tmp=$(pip list|grep google-auth-httplib2|awk '{print $2}')
            if [ "$tmp" != '0.1.0' ];then
                pip uninstall google-auth-httplib2 -y
                pip install -I google-auth-httplib2==0.1.0 -i https://pypi.Python.org/simple
            fi
            tmp=$(pip list|grep google-auth-oauthlib|awk '{print $2}')
            if [ "$tmp" != '0.5.0' ];then
                # pip uninstall google-auth-oauthlib -y
                pip install -I google-auth-oauthlib==0.5.0 -i https://pypi.Python.org/simple
            fi
            tmp=$(pip list|grep -E '^httplib2'|awk '{print $2}')
            if [ "$tmp" != '0.18.1' ];then
                # pip uninstall httplib2 -y
                pip install -I httplib2==0.18.1 -i https://pypi.Python.org/simple
            fi
        else
            pip install -I pyOpenSSL
            pip install -I google-api-python-client==2.39.0 google-auth-httplib2==0.1.0 google-auth-oauthlib==0.5.0 -i https://pypi.Python.org/simple
            pip install -I httplib2==0.18.1 -i https://pypi.Python.org/simple
        fi
        echo '正在安装脚本文件...' > $install_tmp

        mkdir -p $serverPath/gdrive
        echo "${VERSION}" > $serverPath/gdrive/version.pl
        echo '安装完成' > $install_tmp
    else
        echo '服务器连接不上谷歌云！安装失败！' > $install_tmp
        exit 1
    fi
}

Uninstall_App()
{
	rm -rf $serverPath/gdrive
	echo '卸载完成' > $install_tmp
}


action=$1
type=$2

echo $action $type
if [ "${action}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
