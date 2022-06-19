[Unit]
Description=fast remote file copy program daemon
ConditionPathExists={$SERVER_PATH}/rsyncd/rsyncd.conf

[Service]
ExecStart={$RSYNC_BIN} --daemon --no-detach

[Install]
WantedBy=multi-user.target
