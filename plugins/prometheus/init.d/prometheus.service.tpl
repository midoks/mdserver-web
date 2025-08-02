[Unit]
Description=Prometheus
Documentation=https://prometheus.io/docs/introduction/overview/
Wants=network-online.target
After=network-online.target
[Service]
Type=simple
ExecReload=/bin/kill -HUP $MAINPID
ExecStart={$SERVER_PATH}/prometheus/prometheus \
  --config.file={$SERVER_PATH}/prometheus/prometheus.yml \
  --storage.tsdb.path={$SERVER_PATH}/prometheus/data \
  --web.console.templates={$SERVER_PATH}/prometheus/consoles \
  --web.console.libraries={$SERVER_PATH}/prometheus/console_libraries \
  --web.listen-address=0.0.0.0:9090
SyslogIdentifier=prometheus
Restart=always
[Install]
WantedBy=multi-user.target