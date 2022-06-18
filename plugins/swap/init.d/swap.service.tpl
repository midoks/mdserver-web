
[Unit]
Description=Swap Process Manager
After=network.target

[Service]
Type=forking
ExecStart={$SWAPON_BIN} {$SERVER_PATH}/swap/swapfile
ExecReload=/bin/kill -USR2 $MAINPID

[Install]
WantedBy=multi-user.target
