[Unit]
Description=SimplePing Server
After=network.service
After=syslog.target

[Service]
User=root
Group=root
Type=simple
WorkingDirectory={$SERVER_PATH}/simpleping
ExecStart={$SERVER_PATH}/simpleping/simpleping service
ExecReload=/bin/kill -USR2 $MAINPID
PermissionsStartOnly=true
LimitNOFILE=5000
Restart=on-failure
RestartSec=10
RestartPreventExitStatus=1
PrivateTmp=false

[Install]
WantedBy=multi-user.target