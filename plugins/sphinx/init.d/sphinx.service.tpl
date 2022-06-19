[Unit]
Description=Open Source Search Server
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/bin/bin/searchd -c {$SERVER_APP}/sphinx.conf
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target