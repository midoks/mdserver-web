#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
VERSION=$2

cpu_arch=`arch`
if [[ $cpu_arch != "x86_64" ]];then
  echo 'Does not support non-x86 system installation'
  exit 0
fi

# if [ -f "/usr/bin/apt-get" ];then
# 	systemver='ubuntu'
# elif [ -f "/etc/redhat-release" ];then
# 	systemver=`cat /etc/redhat-release|sed -r 's/.* ([0-9]+)\..*/\1/'`
# 	postfixver=`postconf mail_version|sed -r 's/.* ([0-9\.]+)$/\1/'`
# else
# 	echo 'Unsupported system version'
# 	exit 0
# fi

## curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update_dev.sh | bash
## debug:
## cd /www/server/mdserver-web/plugins/mail && bash install.sh install 1.0

bash ${rootPath}/scripts/getos.sh
OSNAME=`cat ${rootPath}/data/osname.pl`
OSNAME_ID=`cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F "\"" '{print $2}'`


Install_debain(){
	hostname=`hostname`
  	# 安装postfix和postfix-sqlite
  	debconf-set-selections <<< "postfix postfix/mailname string ${hostname}"
  	debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
  	apt install postfix -y
  	apt install postfix-sqlite -y
  	apt install sqlite -y

  	# 安装dovecot和dovecot-sieve
  	apt install dovecot-core dovecot-pop3d dovecot-imapd dovecot-lmtpd dovecot-sqlite dovecot-sieve -y

  	apt install rspamd -y

  	apt install cyrus-sasl-plain -y
}

Uninstall_debain(){
	apt remove postfix postfix-sqlite -y && rm -rf /etc/postfix
    dpkg -P postfix postfix-sqlite
    apt remove dovecot-core dovecot-imapd dovecot-lmtpd dovecot-pop3d dovecot-sqlite dovecot-sieve -y
    dpkg -P dovecot-core dovecot-imapd dovecot-lmtpd dovecot-pop3d dovecot-sqlite dovecot-sieve
    apt remove opendkim opendkim-tools -y
    dpkg -P opendkim opendkim-tools
    apt remove rspamd -y
    dpkg -P rspamd
}



Install_App()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source

	if [[ $OSNAME = "centos" ]]; then

		if [[ $OSNAME_ID == "7" ]];then
			Install_centos7
		fi

		if [[ $OSNAME_ID == "8" ]];then
			Install_centos8
		fi

  	elif [[ $OSNAME = "debian" ]]; then
    	Install_debain
  	else
    	Install_ubuntu
  	fi

  	if [ ! -f /etc/dovecot/conf.d/90-sieve.conf ];then
	    if [ -f "/usr/bin/apt-get" ];then
	     	apt install dovecot-sieve -y
	    else
	     	rm -rf /etc/dovecot_back
	      	cp -a /etc/dovecot /etc/dovecot_back
	      	yum remove dovecot -y
	      	yum install dovecot-pigeonhole -y
	      	if [ ! -f /usr/sbin/dovecot ]; then
	        	yum install dovecot -y
	      	fi
	      	\cp -a /etc/dovecot_back/* /etc/dovecot
	      	chown -R vmail:dovecot /etc/dovecot
	      	chmod -R o-rwx /etc/dovecot

	      	systemctl enable dovecot
	      	systemctl restart  dovecot
	    fi
	  fi

  	filesize=`ls -l /etc/dovecot/dh.pem | awk '{print $5}'`
  	echo $filesize

  	if [ ! -f "/etc/dovecot/dh.pem" ] || [ $filesize -lt 300 ]; then
    	openssl dhparam 2048 > /etc/dovecot/dh.pem
  	fi
}

Uninstall_App()
{
	if [[ $OSNAME = "centos" ]]; then

		if [[ $OSNAME_ID == "7" ]];then
			Install_centos7
		fi

		if [[ $OSNAME_ID == "8" ]];then
			Install_centos8
		fi

  	elif [[ $OSNAME = "debian" ]]; then
    	Uninstall_debain
  	else
    	Install_ubuntu
  	fi

	if [ -f $serverPath/mail/initd/mail ];then
		$serverPath/mail/initd/mail stop
	fi

	rm -rf /etc/postfix
	rm -rf /etc/dovecot
	rm -rf /etc/opendkim
	rm -rf /usr/share/rspamd/www/rspamd
	echo "Uninstall_Mail" > $install_tmp
}

action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi
