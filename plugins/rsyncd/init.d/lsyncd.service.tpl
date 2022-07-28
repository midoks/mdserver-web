[Unit]
Description=fast remote file copy program daemon
ConditionPathExists={$SERVER_PATH}/rsyncd/rsyncd.conf

[Service]
ExecStart={$LSYNC_BIN} --config={$SERVER_PATH}/rsyncd/lsyncd.conf --daemon --no-detach

[Install]
WantedBy=multi-user.target
