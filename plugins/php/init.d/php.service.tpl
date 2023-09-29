# It's not recommended to modify this file in-place, because it
# will be overwritten during upgrades.  If you want to customize,
# the best way is to use the "systemctl edit" command.
# systemctl daemon-reload

[Unit]
Description=The PHP {$VERSION} FastCGI Process Manager
After=network.target

[Service]
Environment="LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/www/server/lib/icu/lib"
PIDFile={$SERVER_PATH}/php/{$VERSION}/var/run/php-fpm.pid
ExecStart={$SERVER_PATH}/php/{$VERSION}/sbin/php-fpm --nodaemonize --fpm-config {$SERVER_PATH}/php/{$VERSION}/etc/php-fpm.conf
ExecReload=/bin/kill -USR2 $MAINPID
PrivateTmp=false

[Install]
WantedBy=multi-user.target
