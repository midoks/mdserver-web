# It's not recommended to modify this file in-place, because it
# will be overwritten during upgrades.  If you want to customize,
# the best way is to use the "systemctl edit" command.

[Unit]
Description=The PHP {$VERSION} FastCGI Process Manager
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/php/{$VERSION}/sbin/php-fpm --daemonize --fpm-config {$SERVER_PATH}/php/{$VERSION}/etc/php-fpm.conf
ExecStop=/bin/kill -INT $MAINPID
ExecReload=/bin/kill -USR2 $MAINPID
PrivateTmp=false

[Install]
WantedBy=multi-user.target
