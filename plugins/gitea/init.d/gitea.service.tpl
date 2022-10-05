[Unit]
Description=gitea
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/gitea/init.d/gitea start
ExecStop={$SERVER_PATH}/gitea/init.d/gitea stop
RemainAfterExit=yes
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
