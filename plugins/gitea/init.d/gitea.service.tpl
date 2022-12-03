[Unit]
Description=Gitea (Git with a cup of tea)
After=syslog.target
After=network.target

[Service]
RestartSec=2s
Type=simple
User=www
Group=www
WorkingDirectory={$SERVER_PATH}/gitea
ExecStart={$SERVER_PATH}/gitea/gitea web
Restart=always
Environment=USER=www HOME=/home/www GITEA_WORK_DIR={$SERVER_PATH}/gitea
RemainAfterExit=yes
#AmbientCapabilities=CAP_NET_BIND_SERVICE
#CapabilityBoundingSet=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
