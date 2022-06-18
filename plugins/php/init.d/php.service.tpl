# It's not recommended to modify this file in-place, because it
# will be overwritten during upgrades.  If you want to customize,
# the best way is to use the "systemctl edit" command.

[Unit]
Description=The PHP {$VERSION} FastCGI Process Manager
After=network.target

[Service]
Type=simple
PIDFile={$SERVER_PATH}/php/{$VERSION}/var/run/php-fpm.pid
ExecStart={$SERVER_PATH}/php/{$VERSION}/sbin/php-fpm --nodaemonize --fpm-config {$SERVER_PATH}/php/80/etc/php-fpm.conf
ExecReload=/bin/kill -USR2 $MAINPID
PrivateTmp=true
ProtectSystem=full
PrivateDevices=true
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_NETLINK AF_UNIX
RestrictNamespaces=true

[Install]
WantedBy=multi-user.target
