[Unit]
Description=Apache Web Server
After=network.target

[Service]
Type=simple 
Environment=LANG=C
ExecStart={$SERVER_PATH}/apache/httpd/bin/httpd $OPTIONS -DFOREGROUND
ExecReload={$SERVER_PATH}/apache/httpd/bin/httpd $OPTIONS -k graceful
KillSignal=SIGWINCH

KillMode=mixed
PrivateTmp=true

[Install]
WantedBy=multi-user.target