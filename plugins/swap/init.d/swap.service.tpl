
[Unit]
Description=Swap Process Manager
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/swap/init.d/swap start
ExecStop={$SERVER_PATH}/swap/init.d/swap stop
RemainAfterExit=yes


[Install]
WantedBy=multi-user.target
