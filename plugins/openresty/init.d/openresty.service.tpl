[Unit]
Description=OpenResty is a dynamic web platform based on NGINX and LuaJIT.
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/openresty/bin/openresty -c {$SERVER_PATH}/openresty/nginx/conf/nginx.conf
ExecStop={$SERVER_PATH}/openresty/bin/openresty -s stop
ExecReload={$SERVER_PATH}/openresty/bin/openresty -s reload
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target