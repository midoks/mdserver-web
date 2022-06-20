[Unit]
Description=fast remote file copy program daemon
ConditionPathExists={$SERVER_PATH}/rsyncd/rsyncd.conf

[Service]
ExecStart={$RSYNC_BIN} --config={$SERVER_PATH}/rsyncd/rsyncd.conf --daemon --no-detach

[Install]
WantedBy=multi-user.target
