[Unit]
Description=Loki Log Aggregation System
After=network.target

[Service]
ExecStart={$SERVER_PATH}/loki/bin/loki -config.file={$SERVER_PATH}/loki/conf/loki-config.yaml
Restart=always

[Install]
WantedBy=multi-user.target