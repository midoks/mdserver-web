[Unit]
Description=MySQL Server
After=network.service

[Service]
User=mysql
Group=mysql
Type=forking
ExecStart={$SERVER_PATH}/mysql/bin/mysqld --defaults-file={$SERVER_PATH}/mysql/etc/my.cnf --daemonize
TimeoutSec=0
PermissionsStartOnly=true
LimitNOFILE=5000
Restart=on-failure
RestartSec=10
RestartPreventExitStatus=1
PrivateTmp=false


[Install]
WantedBy=multi-user.target