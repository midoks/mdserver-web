[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/keepalived/sbin/keepalived -D
ExecReload=/bin/kill -USR1 $MAINPID
Restart=on-failure
StandardOutput={$SERVER_PATH}/keepalived/keepalived.log

[Install]
WantedBy=multi-user.target