# It's not recommended to modify this file in-place, because it
# will be overwritten during upgrades.  If you want to customize,
# the best way is to use the "systemctl edit" command.
# systemctl daemon-reload

[Unit]
Description=The PHP {$VERSION} FastCGI Process Manager
After=network.target

[Service]
ExecStart={$SERVER_PATH}/rapira/{$VERSION}/bin/rapira serve {$SERVER_PATH}/rapira/{$VERSION}/rapira.toml
ExecReload=/bin/kill -USR2 $MAINPID
PrivateTmp=false

[Install]
WantedBy=multi-user.target
