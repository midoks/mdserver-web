#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

cpu_arch=`arch`
if [[ $cpu_arch != "x86_64" ]];then
  echo 'Does not support non-x86 system installation'
  exit 0
fi


OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`

Install_centos8()
{
  yum install epel-release -y
  # 卸载系统自带的postfix
  if [[ $cpu_arch = "x86_64" && $postfixver != "3.4.9" ]];then
    yum remove postfix -y
    rm -rf /etc/postfix
  fi
  # 安装postfix和postfix-sqlite
  yum localinstall $pluginPath/rpm/postfix3-3.4.9-1.gf.el8.x86_64.rpm -y
  yum localinstall $pluginPath/rpm/postfix3-sqlite-3.4.9-1.gf.el8.x86_64.rpm -y
  if [[ ! -f "/usr/sbin/postfix" ]]; then
    yum install postfix -y
    yum install postfix-sqlite -y
  fi
  # 安装dovecot和dovecot-sieve
  yum install dovecot-pigeonhole -y
  if [[ ! -f "/usr/sbin/dovecot" ]]; then
    yum install dovecot -y
  fi
  # 安装opendkim
#  安装rspamd
                                          
  install_rspamd
  yum install cyrus-sasl-plain -y
}

Install_centos7() {

    yum install epel-release -y
    # 卸载系统自带的postfix
    if [[ $cpu_arch = "x86_64" && $postfixver != "3.4.7" ]];then
        yum remove postfix -y
     rm -rf /etc/postfix
    fi
    # 安装postfix和postfix-sqlite
    yum localinstall $pluginPath/rpm/postfix3-3.4.7-1.gf.el7.x86_64.rpm -y
    yum localinstall $pluginPath/rpm/postfix3-sqlite-3.4.7-1.gf.el7.x86_64.rpm -y
    if [[ ! -f "/usr/sbin/postfix" ]]; then
        yum install postfix -y
        yum install postfix-sqlite -y
    fi
    # 安装dovecot和dovecot-sieve
    yum install dovecot-pigeonhole -y
    if [[ ! -f "/usr/sbin/dovecot" ]]; then
        yum install dovecot -y
    fi
    #安装rspamd
    install_rspamd
    yum install cyrus-sasl-plain -y

}

install_rspamd() {
    if [[ $systemver = "7" ]];then
        wget -O /etc/yum.repos.d/rspamd.repo https://rspamd.com/rpm-stable/centos-7/rspamd.repo
        rpm --import https://rspamd.com/rpm-stable/gpg.key
        yum makecache
        yum install rspamd -y
    elif [ $systemver = "8" ]; then
        wget -O /etc/yum.repos.d/rspamd.repo https://rspamd.com/rpm-stable/centos-8/rspamd.repo
        rpm --import https://rspamd.com/rpm-stable/gpg.key
        yum makecache
        yum install rspamd -y
    else
        CODENAME=`lsb_release -c -s`
        mkdir -p /etc/apt/keyrings
        wget -O- https://rspamd.com/apt-stable/gpg.key | gpg --dearmor | tee /etc/apt/keyrings/rspamd.gpg > /dev/null
        echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rspamd.gpg] http://rspamd.com/apt-stable/ $CODENAME main" | tee /etc/apt/sources.list.d/rspamd.list
        echo "deb-src [arch=amd64 signed-by=/etc/apt/keyrings/rspamd.gpg] http://rspamd.com/apt-stable/ $CODENAME main"  | tee -a /etc/apt/sources.list.d/rspamd.list
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get --no-install-recommends install rspamd -y
    fi
}

Install_App() {
    if [ "$OSNAME_ID" == "7" ];then
        Install_centos7
    elif [ "$OSNAME_ID" == "8" ];then
        Install_centos8
    fi
}

Uninstall_App()
{
    yum remove postfix -y
    yum remove dovecot -y
    yum remove opendkim -y
    yum remove rspamd -y
    yum remove dovecot-pigeonhole -y
}


action=$1
if [ "${1}" == 'install' ];then
  Install_App
else
  Uninstall_App
fi