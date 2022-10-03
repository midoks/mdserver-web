[Unit]
Description=Gogs
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/gitea/init.d/gitea start
ExecStop={$SERVER_PATH}/gitea/init.d/gitea stop
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
