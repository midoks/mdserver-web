[Unit]
Description=OpenResty is a dynamic web platform based on NGINX and LuaJIT.
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/apache/bin/httpd -c {$SERVER_PATH}/apache/nginx/conf/nginx.conf
ExecStop={$SERVER_PATH}/apache/bin/httpd -s stop
ExecReload={$SERVER_PATH}/apache/bin/httpd -s reload
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target