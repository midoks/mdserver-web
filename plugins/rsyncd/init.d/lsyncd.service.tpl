[Unit]
Description=Lightweight inotify based sync daemon
ConditionPathExists={$SERVER_PATH}/rsyncd/lsyncd.conf

[Service]
ExecStart={$LSYNCD_BIN} -pidfile /var/run/lsyncd.pid {$SERVER_PATH}/rsyncd/lsyncd.conf

[Install]
WantedBy=multi-user.target
