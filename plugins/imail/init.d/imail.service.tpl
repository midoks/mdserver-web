[Unit]
Description=Imail Simple Mail Server
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/imail/init.d/imail start
ExecStop={$SERVER_PATH}/imail/init.d/imail stop
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
