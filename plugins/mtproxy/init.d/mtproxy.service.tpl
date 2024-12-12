[Unit]
Description=MTProxy
After=network.target

[Service]
Type=simple
WorkingDirectory={$SERVER_PATH}/mtproxy
ExecStart={$SERVER_PATH}/mtproxy/mtg/mtg run {$SERVER_PATH}/mtproxy/mt.toml
RestartSec=3
Restart=on-failure
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target