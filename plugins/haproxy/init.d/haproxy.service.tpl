[Unit]
Description=he Reliable, High Performance TCP/HTTP Load Balancer
After=network.target

[Service]
Type=forking
ExecStartPre={$SERVER_PATH}/haproxy/sbin/haproxy -c -f {$SERVER_PATH}/haproxy/haproxy.conf
ExecStart={$SERVER_PATH}/haproxy/sbin/haproxy -Ws -f {$SERVER_PATH}/haproxy/haproxy.conf -p /run/haproxy.pid
ExecReload={$SERVER_PATH}/haproxy/sbin/haproxy -f {$SERVER_PATH}/haproxy/haproxy.conf -c -q
Restart=on-failure

[Install]
WantedBy=multi-user.target