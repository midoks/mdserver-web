# It's not recommended to modify this file in-place, because it
# will be overwritten during upgrades.  If you want to customize,
# the best way is to use the "systemctl edit" command.
# systemctl daemon-reload

[Unit]
Description=Rapira PHP {$VERSION} application server
After=network.target

[Service]
Environment="LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{$SERVER_PATH}/rapira/{$VERSION}/link/lib"
ExecStart={$SERVER_PATH}/rapira/{$VERSION}/bin/rapira serve {$SERVER_PATH}/rapira/{$VERSION}/rapira.toml
ExecReload=/bin/kill -USR2 $MAINPID
PrivateTmp=false

[Install]
WantedBy=multi-user.target
