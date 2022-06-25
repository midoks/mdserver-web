[Unit]
Description=Gogs
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/gogs/init.d/gogs start
ExecStop={$SERVER_PATH}/gogs/init.d/gogs stop
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
