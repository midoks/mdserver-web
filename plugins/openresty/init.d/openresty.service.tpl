[Unit]
Description=OpenResty is a dynamic web platform based on NGINX and LuaJIT.
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/open/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
ExecStop=/usr/local/nginx/sbin/nginx -s stop
ExecReload=/usr/local/nginx/sbin/nginx -s reload
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target