[Unit]
Description=Pure-FTPd is a fast, production-quality, standard-conformant FTP server
After=network.target



[Service]
Type=forking
ExecStart={$SERVER_PATH}/pureftp/sbin/pure-ftpd {$SERVER_PATH}/pureftp/etc/pure-ftpd.conf
ExecStop=/bin/kill -HUP $MAINPID
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target