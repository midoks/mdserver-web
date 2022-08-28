[Unit]
Description=he Reliable, High Performance TCP/HTTP Load Balancer
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/haproxy/sbin/haproxy -c -f {$SERVER_PATH}/haproxy/haproxy.conf
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target