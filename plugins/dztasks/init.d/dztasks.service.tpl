[Unit]
Description=dztasks server
After=network.service
After=syslog.target

[Service]
User=root
Group=root
Type=simple
WorkingDirectory={$SERVER_PATH}/dztasks
ExecStart={$SERVER_PATH}/dztasks/dztasks web
ExecReload=/bin/kill -USR2 $MAINPID
PermissionsStartOnly=true
LimitNOFILE=5000
Restart=on-failure
RestartSec=10
RestartPreventExitStatus=1
PrivateTmp=false

[Install]
WantedBy=multi-user.target