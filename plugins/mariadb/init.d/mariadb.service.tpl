[Unit]
Description=MariaDB Server: The open source relational database
Documentation=https://mariadb.org/download/?t=mariadb
After=network.service
After=syslog.target

[Service]
User=mysql
Group=mysql
Type=simple
ExecStart={$SERVER_PATH}/mariadb/bin/mysqld --defaults-file={$SERVER_PATH}/mariadb/etc/my.cnf
ExecReload=/bin/kill -USR2 $MAINPID
PermissionsStartOnly=true
LimitNOFILE=5000
Restart=on-failure
RestartSec=10
RestartPreventExitStatus=1
PrivateTmp=false


[Install]
WantedBy=multi-user.target