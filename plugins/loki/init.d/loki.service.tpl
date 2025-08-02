[Unit]
Description=Loki Log Aggregation System
After=network.target

[Service]
ExecStart={$SERVER_PATH}/bin/loki -config.file={$SERVER_PATH}/config/loki-config.yaml
Restart=always

[Install]
WantedBy=multi-user.target