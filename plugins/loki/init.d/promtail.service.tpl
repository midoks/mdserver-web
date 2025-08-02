[Unit]
Description=Promtail System
After=network.target

[Service]
ExecStart={$SERVER_PATH}/loki/bin/promtail -config.file={$SERVER_PATH}/loki/conf/promtail-config.yaml
Restart=always

[Install]
WantedBy=multi-user.target