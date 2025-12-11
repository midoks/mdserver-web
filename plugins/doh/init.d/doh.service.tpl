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
# /www/server/doh/doh-proxy -u 127.0.0.1:53 -l 127.0.0.1:3000
# /www/server/doh/doh-proxy -h
ExecStart={$SERVER_PATH}/doh/doh-proxy -u 127.0.0.1:53 -l 127.0.0.1:3000
Restart=always
RemainAfterExit=yes
#AmbientCapabilities=CAP_NET_BIND_SERVICE
#CapabilityBoundingSet=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
