[Unit]
Description=DOH(DNS over HTTPS)
After=syslog.target
After=network.target

[Service]
RestartSec=2s
Type=simple
User=www
Group=www
WorkingDirectory={$SERVER_PATH}/doh
ExecStart={$SERVER_PATH}/doh/doh-proxy --config {$SERVER_PATH}/config.toml
Restart=always
RemainAfterExit=yes
#AmbientCapabilities=CAP_NET_BIND_SERVICE
#CapabilityBoundingSet=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
