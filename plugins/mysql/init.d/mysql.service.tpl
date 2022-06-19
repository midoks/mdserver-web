[Unit]
Description=MySQL Community Server
Documentation=man:mysqld(8)
Documentation=http://dev.mysql.com/doc/refman/en/using-systemd.html
After=network.service
After=syslog.target

[Service]
User=mysql
Group=mysql
Type=forking
ExecStart={$SERVER_PATH}/mysql/bin/mysqld --defaults-file={$SERVER_PATH}/mysql/etc/my.cnf --daemonize
ExecReload=/bin/kill -USR2 $MAINPID
TimeoutSec=0
PermissionsStartOnly=true
LimitNOFILE=5000
Restart=on-failure
RestartSec=10
RestartPreventExitStatus=1
PrivateTmp=false


[Install]
WantedBy=multi-user.target