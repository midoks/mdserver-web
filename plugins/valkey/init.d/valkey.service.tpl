[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/valkey/bin/valkey-server {$SERVER_PATH}/valkey/valkey.conf
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target