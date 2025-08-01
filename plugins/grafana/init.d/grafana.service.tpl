[Unit]
Description=Grafana instance
Documentation=http://docs.grafana.org
After=network-online.target
[Service]
Type=simple
User=grafana
Group=grafana
Restart=on-failure
ExecStart={$SERVER_PATH}/bin/grafana server --config={$SERVER_PATH}/grafana/conf/defa.defaults --homepath={$SERVER_PATH}/grafana

[Install]
WantedBy=multi-user.target