# It's not recommended to modify this file in-place, because it
# will be overwritten during upgrades.  If you want to customize,
# the best way is to use the "systemctl edit" command.

[Unit]
Description=The PHP {$VERSION} FastCGI Process Manager
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/php/init.d/php{$VERSION} start
ExecStop={$SERVER_PATH}/php/init.d/php{$VERSION} stop
ExecReload={$SERVER_PATH}/php/init.d/php{$VERSION} reload
PrivateTmp=false

[Install]
WantedBy=multi-user.target
