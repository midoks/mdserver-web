[Unit]
Description=Grafana instance
Documentation=http://docs.grafana.org
After=network-online.target
[Service]
Type=simple
Restart=on-failure
ExecStart={$SERVER_PATH}/bin/grafana server --config={$SERVER_PATH}/grafana/conf/grafana.ini --homepath={$SERVER_PATH}/grafana/data

[Install]
WantedBy=multi-user.target