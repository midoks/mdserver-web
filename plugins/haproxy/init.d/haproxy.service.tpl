[Unit]
Description=he Reliable, High Performance TCP/HTTP Load Balancer
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/sphinx/bin/bin/searchd -c {$SERVER_PATH}/sphinx/sphinx.conf
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target